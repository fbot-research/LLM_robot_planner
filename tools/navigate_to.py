from pydantic import BaseModel, Field
from tool_registry import tool
from robot_state import update_state
import random
import math

class NavigateToSchema(BaseModel):
    x: float = Field(..., description="Target x coordinate")
    y: float = Field(..., description="Target y coordinate")
    z: float = Field(..., description="Target z coordinate")
    orientation: list[float] = Field(..., description="Quaternion [x, y, z, w]")

@tool(args_schema=NavigateToSchema)
def navigate_to(x: float, y: float, z: float, orientation: list[float]):
    """Navigate the robot to a specified pose using Nav2.
    
    Plans and executes autonomous navigation to the target pose in the target frame.
    Returns Nav2 navigation feedback and status.
    
    Args:
        x: Target x coordinate in map frame
        y: Target y coordinate in map frame
        z: Target z coordinate in map frame
        orientation: Quaternion orientation [x, y, z, w]
    
    Returns:
        dict: Nav2 navigation result with path planning details and execution status
    """
    try:
        global _robot_state
        
        # Validate orientation
        if len(orientation) != 4:
            return {
                "nav_status": "FAILED",
                "error": "Invalid quaternion format",
                "__control__": "error"
            }
        
        quat_magnitude = sum(q**2 for q in orientation) ** 0.5
        if abs(quat_magnitude - 1.0) > 0.1:
            return {
                "nav_status": "FAILED",
                "error": "Quaternion not normalized",
                "__control__": "error"
            }
        
        # Simulate path planning
        planning_time = random.uniform(0.2, 1.5)
        num_waypoints = max(3, int(distance * 3) + random.randint(2, 5)) if (distance := math.sqrt((x)**2 + (y)**2)) else 3
        distance = math.sqrt(x**2 + y**2)
        path_length = distance + random.uniform(0.1, 0.5)  # Account for non-straight paths
        estimated_time = path_length / random.uniform(0.4, 0.8)  # Speed 0.4-0.8 m/s
        
        # Update shared robot state on successful navigation
        update_state('current_position', {'x': x, 'y': y, 'z': z})
        update_state('current_orientation', {'x': orientation[0], 'y': orientation[1], 'z': orientation[2], 'w': orientation[3]})
        
        # Return authentic Nav2 response
        return {
            "nav_status": "SUCCEEDED",
            "status_code": 4,  # NavGoalResponse NAV_STATUS_SUCCEEDED
            "planning": {
                "planner_name": "GridBased",
                "planning_time": round(planning_time, 3),
                "path_found": True,
                "path": {
                    "header": {
                        "frame_id": "map",
                        "seq": random.randint(100, 1000)
                    },
                    "poses": num_waypoints
                }
            },
            "navigation": {
                "distance_traveled": round(path_length, 2),
                "execution_time": round(estimated_time + random.uniform(0.5, 2.0), 2),
                "obstacles_detected": random.choice([0, 0, 0, 1]) if random.random() < 0.1 else 0,
                "replans": random.randint(0, 2),
                "max_speed": round(random.uniform(0.4, 0.8), 2)
            },
            "final_pose": {
                "position": {"x": x, "y": y, "z": z},
                "orientation": {"x": orientation[0], "y": orientation[1], "z": orientation[2], "w": orientation[3]},
                "frame_id": "map"
            },
            "__control__": "done"
        }
    
    except Exception as e:
        return {
            "nav_status": "FAILED",
            "error": str(e),
            "status_code": 5,  # FAILED status
            "__control__": "error"
        }
