from pydantic import BaseModel, Field
from tool_registry import tool

class GripperCommand(BaseModel):
    pass  # No parameters needed for this simple command

@tool(args_schema=GripperCommand)
def close_gripper():
    """Close the robot's gripper.
    
    Sends a command to close the end-effector gripper, typically used for
    grasping or holding objects. The gripper will close until it reaches
    full closure or encounters resistance from a grasped object.
    
    Returns:
        dict: Status of the gripper closing operation.
    """
    print("Gripper closed.")
    return {"status": "success", '__control__': 'done'}

@tool(args_schema=GripperCommand)
def open_gripper():
    """Open the robot's gripper.
    
    Sends a command to open the end-effector gripper, typically used for
    releasing objects or preparing for a new grasp. The gripper will open
    until fully extended.
    
    Returns:
        dict: Status of the gripper opening operation.
    """
    print("Gripper opened.")
    return {"status": "success", '__control__': 'done'}