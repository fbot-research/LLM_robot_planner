from pydantic import BaseModel, Field
from tool_registry import tool

class GripperCommand(BaseModel):
    pass  # No parameters needed for this simple command

@tool(args_schema=GripperCommand)
def close_gripper():
    print("Gripper closed.")
    return {"status": "success", '__control__': 'continue'}

@tool(args_schema=GripperCommand)
def open_gripper():
    print("Gripper opened.")
    return {"status": "success", '__control__': 'continue'}