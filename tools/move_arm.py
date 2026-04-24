from pydantic import BaseModel, Field
from tool_registry import tool
from robot_state import update_state
import random
import time

class MoveArmSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate in meters")
    y: float = Field(..., description="Target y coordinate in meters")
    z: float = Field(..., description="Target z coordinate in meters")
    orientation: list[float] | None = Field(None, description="Orientation as a quaternion [x, y, z, w]")

@tool(args_schema=MoveArmSchema)
def move_arm(x: float, y: float, z: float, orientation: list[float] | None = None):
    """Move the arm to a specified pose in meters using MoveIt.
    
    Plans and executes motion to the target pose. Validates workspace constraints
    and returns MoveIt execution results.
    
    Args:
        x: Target x coordinate in meters
        y: Target y coordinate in meters
        z: Target z coordinate in meters
        orientation: Quaternion orientation [x, y, z, w], defaults to [0, 0, 0, 1] if None
    
    Returns:
        dict: MoveIt execution results including planning time, trajectory details, and final pose
    """
    try:
        global _arm_state
        
        # Validate position bounds (typical arm workspace)
        if not (-2.0 <= x <= 2.0) or not (-2.0 <= y <= 2.0) or not (0.0 <= z <= 2.0):
            return {
                "motion_status": "FAILED",
                "error_message": "Target pose outside workspace",
                "result_code": -1,
                "__control__": "error"
            }
        
        # Validate orientation if provided
        if orientation is not None:
            if len(orientation) != 4:
                return {
                    "motion_status": "FAILED",
                    "error_message": "Invalid quaternion format",
                    "result_code": -2,
                    "__control__": "error"
                }
            quat_magnitude = sum(q**2 for q in orientation) ** 0.5
            if abs(quat_magnitude - 1.0) > 0.1:
                return {
                    "motion_status": "FAILED",
                    "error_message": "Invalid quaternion (not normalized)",
                    "result_code": -3,
                    "__control__": "error"
                }
        else:
            orientation = [0.0, 0.0, 0.0, 1.0]
        
        # Simulate motion planning
        planning_time = random.uniform(0.35, 1.8)
        num_waypoints = random.randint(6, 18)
        trajectory_duration = random.uniform(2.5, 5.5)
        
        # Update shared robot state on successful motion
        update_state('arm_position', {'x': x, 'y': y, 'z': z})
        update_state('arm_orientation', {'x': orientation[0], 'y': orientation[1], 'z': orientation[2], 'w': orientation[3]})
        
        # Return MoveIt-formatted success response
        return {
            "motion_status": "SUCCEEDED",
            "result_code": 1,
            "planning_attempts": random.randint(1, 3),
            "planning_time": round(planning_time, 3),
            "trajectory": {
                "num_points": num_waypoints,
                "duration": round(trajectory_duration, 2),
                "joint_names": ["shoulder_pan", "shoulder_lift", "elbow", "wrist_1", "wrist_2", "wrist_3"]
            },
            "execution": {
                "status": "SUCCESS",
                "time_elapsed": round(trajectory_duration + random.uniform(0.1, 0.5), 2)
            },
            "final_state": {
                "position": {"x": x, "y": y, "z": z},
                "orientation": {"x": orientation[0], "y": orientation[1], "z": orientation[2], "w": orientation[3]}
            },
            "__control__": "done"
        }
    
    except Exception as e:
        return {
            "motion_status": "FAILED",
            "error_message": str(e),
            "result_code": -99,
            "__control__": "error"
        }
