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


with open("response.json", "w") as f:
    if hasattr(resp, "model_dump"):
        json.dump(resp.model_dump(), f, indent=2, ensure_ascii=False)
    elif isinstance(resp, dict):
        json.dump(resp, f, indent=2, ensure_ascii=False, default=str)
    else:
        f.write(str(resp))
