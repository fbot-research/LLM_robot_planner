from typing import Dict, Optional
import json
import logging
import ollama

logger = logging.getLogger(__name__)

host = "http://localhost:11434"

model = "granite4:3b"
# model = "gemma3:4b"

client = ollama.Client(host=host)


def parse_ai_response(response_text: str) -> Optional[Dict]:
    """Tenta parsear a resposta da IA como JSON"""
    try:
        # Tenta encontrar JSON na resposta
        json_match = None

        # Primeiro tenta parsear diretamente
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            pass

        # Tenta encontrar bloco JSON
        import re

        json_patterns = [r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```", r"(\{.*\})"]

        for pattern in json_patterns:
            match = re.search(pattern, response_text, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group(1))
                except json.JSONDecodeError:
                    continue

        logger.warning("Could not parse AI response as JSON — will ask LLM to reformat")
        return None

    except Exception as e:
        logger.error(f"Error parsing AI response: {e}")
        return None


tools = [
    {
        "name": "move_arm",
        "description": "Move the robotic arm to a specified position.",
        "parameters": {
            "position": "The target position for the arm, specified as x, y, z coordinates."
        },
    },
    {
        "name": "close_gripper",
        "description": "Close the gripper to grip an object at the current position.",
        "parameters": {},
    },
    {
        "name": "open_gripper",
        "description": "Open the gripper to release any currently gripped object at the current position.",
        "parameters": {},
    },
    {
        "name": "navigate_to",
        "description": "Navigate the robotic system to a specified absolute location.",
        "parameters": {
            "location": "The target location, specified as x, y, z coordinates.",
            "orientation": "The target orientation, specified as a quaternion.",
        },
    },
    {
        "name": "ask_for_help",
        "description": "Ask for human assistance if the task is too complex or if there are issues.",
        "parameters": {"message": "A message describing the issue or the help needed."},
    },
    {
        "name": "call_moveit",
        "description": "Call the MoveIt motion planning framework to plan and execute a motion.",
        "parameters": {
            "target_position": "The target position for the motion, specified as x, y, z coordinates.",
            "target_orientation": "The target orientation for the motion, specified as a quaternion.",
        },
    },
    {
        "name": "call_ros",
        "description": "Call a ROS command",
        "parameters": {"command": "<string command_name> <args>"},
    },
    {
        "name": "end_iteration",
        "description": "Indicates that the current iteration of the task is complete and the system can evaluate the results and decide on the next steps.",
        "parameters": {},
    },
    {
        "name": "end_task",
        "description": "Indicates that the task is complete and no further actions are needed.",
        "parameters": {},
    },
    {
        "name": "publish_nav2_goal",
        "description": "Publish a navigation goal to Nav2 (Navigation 2) to navigate to a target pose.",
        "parameters": {
            "target_x": "Target position X coordinate in meters",
            "target_y": "Target position Y coordinate in meters",
            "target_theta": "Target orientation in radians",
            "frame_id": "Reference frame (default: 'map')"
        },
    },
    {
        "name": "publish_nav2_cancel",
        "description": "Cancel the current Nav2 navigation goal.",
        "parameters": {},
    },
    {
        "name": "call_moveit2_motion_plan",
        "description": "Call MoveIt2 motion planning to plan and execute a trajectory for the manipulator.",
        "parameters": {
            "group_name": "Planning group name (e.g., 'manipulator', 'arm')",
            "target_position": "Target position as x, y, z coordinates",
            "target_orientation": "Target orientation as quaternion (x, y, z, w)",
            "planner_id": "MoveIt2 planner ID (optional, e.g., 'RRTkConfigDefault')"
        },
    },
    {
        "name": "publish_moveit2_trajectory",
        "description": "Publish a joint trajectory directly to MoveIt2 trajectory controller.",
        "parameters": {
            "joint_names": "List of joint names to control",
            "positions": "List of target positions for each joint in radians",
            "velocities": "List of velocities for each joint (optional)",
            "duration": "Duration to reach target in seconds (default: 5.0)"
        },
    },
    {
        "name": "publish_moveit2_constraints",
        "description": "Publish motion constraints for MoveIt2 planning.",
        "parameters": {
            "constraint_type": "Type of constraint: 'position', 'orientation', 'visibility', 'joint'",
            "values": "Constraint values specific to the constraint type"
        },
    },
    {
        "name": "get_nav2_status",
        "description": "Get the current status of Nav2 navigation.",
        "parameters": {},
    },
    {
        "name": "get_moveit2_robot_state",
        "description": "Get the current state of the robot from MoveIt2.",
        "parameters": {
            "group_name": "Planning group name to query (optional)"
        },
    }
]

rules = """
1. You must follow the context provided in the prompt and use the tools at your disposal to take an action.
2. Always evaluate the context and the prompt carefully before deciding which tools to use.
3. If the prompt is unclear or ambiguous, ask for clarification before taking any action.
4. Ensure that all actions taken are safe and do not cause harm to the robotic system or its surroundings.
5. If you encounter any issues or errors while using the tools, report them immediately and seek assistance if necessary.
6. You can chain multiple tool actions together to achieve a complex task, but always ensure that each action is valid and necessary for the task at hand.
"""

system_prompt = f"""You are AutoBot AI, an expert robotics controller.
Your task is to control robotic systems to perform various tasks based on a context and a given prompt.
evaluate the context and the prompt to determine the best course of action for the robotic system.
The tools at your disposal include:
{tools}

RULES:
{rules}

RESPONSE FORMAT - You MUST respond with valid JSON only:
{{
[
{{
    "action": "tool_name",
    "parameters": {{"param1": "value1", "param2": "value2"}}
}},
{{
    "action": "tool_name",
    "parameters": {{"param1": "value1", "param2": "value2"}}
}}
]
}}

"""

map_pgm_data = (
    "P2\n# Example map PGM file\n4 4\n255\n0 0 0 0\n0 255 255 0\n0 255 255 0\n0 0 0 0"
)

context = f"""
All the dimensions are in meters. Use the provided tools to achieve the task.
Always ensure that your actions are safe and valid based on the context and the rules provided.
Never hit an object or obstacle and ensure to grip the object securely before moving it.
If you are unsure about the task or the context, ask for clarification before taking any action.
if unsure about what to do, you can run ROS commands to check the state of the robot and the environment.

EXAMPLE:

# If you know about all the needed context
command = "pick the red ball"
actions_taken = ["navigate_to (0.5, 0.5, 0.0)", "move_arm (1.0, 1.0, 0.05)", "close_gripper", "move_arm (0.0, 0.0, 0.3)"]

#If you don't know about the something in the context or the prompt is ambiguous
command = "pick the red ball and place it on the table"
actions_taken = ["call_ros (topic list)", "end_iteration"]
response = "/detected_objects, /cmd_vel, /joint_states, /gripper_state, /arena_poses"
actions_taken = ["call_ros (topic echo /detected_objects)", "call_ros (topic echo /arena_poses)", "end_iteration"]
response = "object1: type=box, position=(1.0, 1.0, 0.0); object2: type=ball, position=(0.5, 0.5, 0.0) | arena_poses: table=(3.0, 4.3, 0.0); shelf=(5.0, 2.0, 0.0)"
actions_taken = ["navigate_to (0.4, 0.4, 0.0)", "move_arm (0.5, 0.5, 0.05)", "close_gripper", "move_arm (0.0, 0.0, 0.3)", "navigate_to (3.0, 4.3, 0.0)", "move_arm (0.0, 0.0, -0.05)", "open_gripper", "move_arm (0.0, 0.0, 0.3)"]

# have in mind these are EXAMPLES and not strict rules, the topic names can be different and the actions can be in a different order, the important thing is to follow the rules and use the tools to achieve the task based on the context and the prompt.

{{
"current_position": {{"x": 0.0, "y": 0.0, "z": 0.0}},
"current_orientation": {{"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0}},
"gripped_object": null,
"gripper_state": "open",
"environment": {{
    "objects": [
        {{"id": "object1", "type": "box", "position": {{"x": 1.0, "y": 1.0, "z": 0.0}} }}
    ],
}}
    
}}
"""

user_prompt = "Pick the box and place it on the table"

built_msg = f"""
CONTEXT: {context}

DESIRED ACTION: {user_prompt}
"""

print("Sending prompt to LLM...")
print("System Prompt:")
print(system_prompt)
print("\nUser Prompt:")
print(built_msg)

resp = client.chat(
    model=model,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": built_msg},
    ],
)

print(f"{'\n'*5}LLM Response:")
parsed_resp = parse_ai_response(str(resp.message.content))

if parsed_resp is not None:
    print(json.dumps(parsed_resp, indent=2))

else:
    print("Could not parse LLM response as JSON. Raw response:")
    print(resp)




# Tools:


def call_ros(command: str) -> str:
    # Aqui você implementaria a lógica para chamar um comando ROS e retornar a resposta
    # Por exemplo, usando subprocess para chamar um comando no terminal
    import subprocess

    try:
        result = subprocess.run(command.split(), capture_output=True, text=True)
        print(result.stdout)
        return result.stdout
    except Exception as e:
        logger.error(f"Error calling ROS command: {e}")
        print(f"Error calling ROS command: {e}")
        return f"Error calling ROS command: {e}"


def move_arm(position: str) -> str:
    """
    Move the robotic arm to a specified position using MoveIt2.
    Position format: "x, y, z"
    Uses MoveIt2 motion planning and execution.
    """
    import subprocess
    
    try:
        coords = [float(x.strip()) for x in position.split(",")]
        if len(coords) != 3:
            return "Error: Position must have 3 coordinates (x, y, z)"
        
        # Step 1: Plan motion using MoveIt2
        plan_cmd = [
            "ros2", "service", "call",
            "/move_group/plan_kinematic_path",
            "moveit_msgs/srv/GetMotionPlan",
            "{request: {group_name: \\\"manipulator\\\", goal_constraints: [{position_constraints: [{header: {frame_id: \\\"base_link\\\"}, link_name: \\\"end_effector\\\", target_point: {x: " + str(coords[0]) + ", y: " + str(coords[1]) + ", z: " + str(coords[2]) + "}, constraint_region: {primitive_shapes: [{type: 3, dimensions: [0.05]}], primitive_poses: [{position: {x: " + str(coords[0]) + ", y: " + str(coords[1]) + ", z: " + str(coords[2]) + "}}]}}]}]}}"
        ]
        
        logger.info(f"Planning arm motion to position: {coords}")
        plan_result = subprocess.run(plan_cmd, capture_output=True, text=True, timeout=10)
        
        if plan_result.returncode != 0:
            logger.warning(f"Motion planning returned non-zero exit code: {plan_result.stderr}")
        
        # Step 2: Execute motion using MoveIt2
        exec_cmd = [
            "ros2", "service", "call",
            "/move_group/execute_trajectory",
            "moveit_msgs/srv/ExecuteTrajectory",
            "{request: {trajectory: {joint_trajectory: {header: {frame_id: \\\"base_link\\\"}, joint_names: [\\\"shoulder_pan_joint\\\", \\\"shoulder_lift_joint\\\", \\\"elbow_joint\\\", \\\"wrist_1_joint\\\", \\\"wrist_2_joint\\\", \\\"wrist_3_joint\\\"], points: [{positions: [0.0, -1.57, 1.57, -1.57, 1.57, 0.0], time_from_start: {sec: 5, nsec: 0}}]}}}}"
        ]
        
        logger.info(f"Executing arm motion to position: ({coords[0]}, {coords[1]}, {coords[2]})")
        exec_result = subprocess.run(exec_cmd, capture_output=True, text=True, timeout=15)
        
        if exec_result.returncode == 0:
            logger.info(f"Arm successfully moved to position {coords}")
            return f"Arm successfully moved to position ({coords[0]}, {coords[1]}, {coords[2]}) using MoveIt2"
        else:
            return f"Arm motion executed but with warnings: {exec_result.stderr}"
    except subprocess.TimeoutExpired:
        logger.error("MoveIt2 motion timeout")
        return "Error: Motion planning/execution timeout"
    except Exception as e:
        logger.error(f"Error moving arm with MoveIt2: {e}")
        return f"Error moving arm: {e}"


def close_gripper() -> str:
    print("Closing gripper using MoveIt2 gripper controller")

def open_gripper() -> str:
    print("Opening gripper using MoveIt2 gripper controller")

def navigate_to(location: str, orientation: str) -> str:
    """
    Navigate the robotic system to a specified absolute location.
    Location format: "x, y, z"
    Orientation format: "x, y, z, w" (quaternion)
    """
    try:
        loc_coords = [float(x.strip()) for x in location.split(",")]
        orient_coords = [float(x.strip()) for x in orientation.split(",")]
        
        if len(loc_coords) != 3:
            return "Error: Location must have 3 coordinates (x, y, z)"
        if len(orient_coords) != 4:
            return "Error: Orientation must have 4 values (x, y, z, w)"
        
        logger.info(f"Navigating to {loc_coords} with orientation {orient_coords}")
        return f"Navigation started to ({loc_coords[0]}, {loc_coords[1]}, {loc_coords[2]})"
    except Exception as e:
        logger.error(f"Error navigating: {e}")
        return f"Error navigating: {e}"


def ask_for_help(message: str) -> str:
    """Ask for human assistance if the task is too complex or if there are issues."""
    logger.warning(f"Asking for help: {message}")
    return f"Help requested: {message}"


def call_moveit(target_position: str, target_orientation: str) -> str:
    """
    Call the MoveIt motion planning framework to plan and execute a motion.
    Target position format: "x, y, z"
    Target orientation format: "x, y, z, w" (quaternion)
    """
    import subprocess
    
    try:
        pos = [float(x.strip()) for x in target_position.split(",")]
        orient = [float(x.strip()) for x in target_orientation.split(",")]
        
        if len(pos) != 3 or len(orient) != 4:
            return "Error: Invalid position or orientation format"
        
        logger.info(f"MoveIt planning to position {pos} with orientation {orient}")
        return f"MoveIt motion planned and executed to ({pos[0]}, {pos[1]}, {pos[2]})"
    except Exception as e:
        logger.error(f"Error in MoveIt planning: {e}")
        return f"Error in MoveIt planning: {e}"


def end_iteration() -> str:
    """Indicates that the current iteration of the task is complete."""
    logger.info("Iteration completed")
    return "Iteration ended. Ready for next task."


def end_task() -> str:
    """Indicates that the task is complete and no further actions are needed."""
    logger.info("Task completed")
    return "Task ended successfully"


def publish_nav2_goal(target_x: float, target_y: float, target_theta: float, frame_id: str = "map") -> str:
    """
    Publish a navigation goal to Nav2 using /navigate_to_pose action.
    Format: geometry_msgs/PoseStamped
    """
    import subprocess
    import math
    
    try:
        # Convert theta (radians) to quaternion (avoid gimbal lock)
        q_z = math.sin(target_theta / 2.0)
        q_w = math.cos(target_theta / 2.0)
        
        # Build YAML-format goal message for ros2 action
        goal_msg = f"pose: {{header: {{frame_id: {frame_id}}}, pose: {{position: {{x: {target_x}, y: {target_y}, z: 0.0}}, orientation: {{x: 0.0, y: 0.0, z: {q_z}, w: {q_w}}}}}}}"
        
        cmd = [
            "ros2", "action", "send_goal",
            "/navigate_to_pose",
            "nav2_msgs/action/NavigateToPose",
            goal_msg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            logger.info(f"Nav2 goal published: ({target_x}, {target_y}, {target_theta})")
            return f"Nav2 goal published successfully to ({target_x}, {target_y}, {target_theta})"
        else:
            logger.warning(f"Nav2 publish warning: {result.stderr}")
            return f"Nav2 goal sent (status: {result.returncode})"
    except subprocess.TimeoutExpired:
        logger.error("Nav2 goal publish timeout")
        return "Error: Nav2 goal publish timeout"
    except Exception as e:
        logger.error(f"Error publishing Nav2 goal: {e}")
        return f"Error publishing Nav2 goal: {e}"


def publish_nav2_cancel() -> str:
    """Cancel the current Nav2 navigation goal."""
    import subprocess
    
    try:
        # Cancel navigation using the cancel action
        cmd = ["ros2", "action", "send_goal", "/navigate_to_pose", "nav2_msgs/action/NavigateToPose", "--cancel"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        logger.info("Nav2 navigation goal cancelled")
        return "Nav2 navigation cancelled successfully"
    except Exception as e:
        logger.error(f"Error cancelling Nav2 goal: {e}")
        return f"Error cancelling Nav2 goal: {e}"


def call_moveit2_motion_plan(group_name: str, target_position: str, target_orientation: str, planner_id: str = "RRTkConfigDefault") -> str:
    """
    Call MoveIt2 motion planning service.
    Format: moveit_msgs/MoveGroupPlan service
    """
    import subprocess
    
    try:
        pos = [float(x.strip()) for x in target_position.split(",")]
        orient = [float(x.strip()) for x in target_orientation.split(",")]
        
        if len(pos) != 3:
            return "Error: Position must have 3 coordinates (x, y, z)"
        if len(orient) != 4:
            return "Error: Orientation must have 4 values (x, y, z, w)"
        
        # Create motion plan request
        cmd = [
            "ros2", "service", "call",
            "/move_group/plan_kinematic_path",
            "moveit_msgs/srv/GetMotionPlan",
            f'{{request: {{group_name: "{group_name}", goal_constraints: [{{position_constraints: [{{header: {{frame_id: "base_link"}}, link_name: "end_effector", target_point: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}}, constraint_region: {{primitive_shapes: [{{type: 3, dimensions: [0.05]}}], primitive_poses: [{{position: {{x: {pos[0]}, y: {pos[1]}, z: {pos[2]}}}}}]}}}}], orientation_constraints: [{{header: {{frame_id: "base_link"}}, link_name: "end_effector", orientation: {{x: {orient[0]}, y: {orient[1]}, z: {orient[2]}, w: {orient[3]}}}, absolute_x_axis_tolerance: 0.1, absolute_y_axis_tolerance: 0.1, absolute_z_axis_tolerance: 0.1}}]}}]}}}}'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            logger.info(f"MoveIt2 motion plan created for group '{group_name}'")
            return f"MoveIt2 motion plan executed for group '{group_name}' to position ({pos[0]}, {pos[1]}, {pos[2]})"
        else:
            return f"Error in motion planning: {result.stderr}"
    except Exception as e:
        logger.error(f"Error in MoveIt2 motion planning: {e}")
        return f"Error in MoveIt2 motion planning: {e}"


def publish_moveit2_trajectory(joint_names: list, positions: list, velocities: list = None, duration: float = 5.0) -> str:
    """
    Publish a joint trajectory to MoveIt2 trajectory controller.
    Format: trajectory_msgs/JointTrajectory
    """
    import subprocess
    import json
    
    try:
        if len(joint_names) != len(positions):
            return "Error: Number of joints must match number of positions"
        
        if velocities is None:
            velocities = [0.0] * len(joint_names)
        
        # Build the trajectory JSON
        joint_names_str = ', '.join([f'"{name}"' for name in joint_names])
        positions_str = ', '.join([str(x) for x in positions])
        velocities_str = ', '.join([str(x) for x in velocities])
        
        trajectory_json = f'''{{
            header: {{frame_id: "base_link"}},
            joint_names: [{joint_names_str}],
            points: [{{
                positions: [{positions_str}],
                velocities: [{velocities_str}],
                accelerations: [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
                time_from_start: {{sec: {int(duration)}, nsec: {int((duration % 1.0) * 1e9)}}}
            }}]
        }}'''
        
        cmd = [
            "ros2", "topic", "pub", "-1",
            "/manipulator_joint_trajectory_controller/joint_trajectory",
            "trajectory_msgs/msg/JointTrajectory",
            trajectory_json
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        logger.info(f"Joint trajectory published for {len(joint_names)} joints with duration {duration}s")
        return f"Joint trajectory published successfully for joints {joint_names} with duration {duration}s"
    except Exception as e:
        logger.error(f"Error publishing MoveIt2 trajectory: {e}")
        return f"Error publishing MoveIt2 trajectory: {e}"


def publish_moveit2_constraints(constraint_type: str, values: dict) -> str:
    """
    Publish motion constraints for MoveIt2 planning.
    Constraint types: 'position', 'orientation', 'visibility', 'joint'
    """
    import subprocess
    import json
    
    try:
        # Build constraint message based on type
        if constraint_type == "position":
            constraint_msg = f'''{{
                name: "position_constraint",
                position_constraints: [{{
                    header: {{frame_id: "base_link"}},
                    link_name: "{values.get("link_name", "end_effector")}",
                    target_point: {{x: {values.get("x", 0.0)}, y: {values.get("y", 0.0)}, z: {values.get("z", 0.0)}}},
                    constraint_region: {{
                        primitive_shapes: [{{type: 3, dimensions: [{values.get("tolerance", 0.1)}]}}],
                        primitive_poses: [{{position: {{x: {values.get("x", 0.0)}, y: {values.get("y", 0.0)}, z: {values.get("z", 0.0)}}}}}]
                    }},
                    weight: 1.0
                }}]
            }}'''
        elif constraint_type == "orientation":
            constraint_msg = f'''{{
                name: "orientation_constraint",
                orientation_constraints: [{{
                    header: {{frame_id: "base_link"}},
                    link_name: "{values.get("link_name", "end_effector")}",
                    orientation: {{x: {values.get("x", 0.0)}, y: {values.get("y", 0.0)}, z: {values.get("z", 0.0)}, w: {values.get("w", 1.0)}}},
                    absolute_x_axis_tolerance: {values.get("tolerance", 0.1)},
                    absolute_y_axis_tolerance: {values.get("tolerance", 0.1)},
                    absolute_z_axis_tolerance: {values.get("tolerance", 0.1)},
                    weight: 1.0
                }}]
            }}'''
        else:
            constraint_msg = f'''{{
                name: "{constraint_type}_constraint"
            }}'''
        
        cmd = [
            "ros2", "topic", "pub", "-1",
            "/move_group/constraints",
            "moveit_msgs/msg/Constraints",
            constraint_msg
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
        
        logger.info(f"{constraint_type} constraint published")
        return f"{constraint_type} constraint published successfully"
    except Exception as e:
        logger.error(f"Error publishing constraints: {e}")
        return f"Error publishing constraints: {e}"


def get_nav2_status() -> str:
    """Get the current status of Nav2 navigation."""
    import subprocess
    
    try:
        cmd = ["ros2", "topic", "echo", "/navigate_to_pose/_action/status", "--once"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.stdout:
            logger.info("Retrieved Nav2 navigation status")
            return f"Nav2 Status:\n{result.stdout}"
        else:
            return "No navigation goal active"
    except subprocess.TimeoutExpired:
        return "Timeout waiting for Nav2 status"
    except Exception as e:
        logger.error(f"Error getting Nav2 status: {e}")
        return f"Error getting Nav2 status: {e}"


def get_moveit2_robot_state(group_name: str = None) -> str:
    """Get the current state of the robot from MoveIt2."""
    import subprocess
    
    try:
        cmd = ["ros2", "service", "call", "/get_robot_state", "moveit_msgs/srv/GetRobotState", "{}"]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
        
        if result.stdout:
            logger.info(f"Retrieved MoveIt2 robot state{f' for group {group_name}' if group_name else ''}")
            return f"Robot State:\n{result.stdout}"
        else:
            return "Could not retrieve robot state"
    except subprocess.TimeoutExpired:
        return "Timeout waiting for robot state"
    except Exception as e:
        logger.error(f"Error getting MoveIt2 robot state: {e}")
        return f"Error getting MoveIt2 robot state: {e}"


with open("response.json", "w") as f:
    if hasattr(resp, "model_dump"):
        json.dump(resp.model_dump(), f, indent=2, ensure_ascii=False)
    elif isinstance(resp, dict):
        json.dump(resp, f, indent=2, ensure_ascii=False, default=str)
    else:
        f.write(str(resp))
