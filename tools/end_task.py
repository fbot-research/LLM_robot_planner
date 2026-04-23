from pydantic import BaseModel, Field
from tool_registry import tool
from typing import Optional

class EndTaskSchema(BaseModel):
    commands: Optional[list[str]] = Field(None, description="List of commands executed to accomplish the task")

@tool(args_schema=EndTaskSchema)
def end_task(commands: Optional[list[str]] = None):
    """Mark the completion of the current task.
    
    Signals that the task has been successfully completed. Optionally accepts
    a list of commands or steps executed during the task for logging and
    verification purposes.
    
    Args:
        commands: Optional list of command strings executed to accomplish the task.
    
    Returns:
        dict: Status with control directive to end task.
    """
    print("Task completed with the following commands:")
    if commands:
        for command in commands:
            print(f"  - {command}")
    return {"status": "success", '__control__': 'end_task'}
