from pydantic import BaseModel, Field
from tool_registry import tool

class EndTaskSchema(BaseModel):
    pass  # No parameters needed for this simple command

@tool(args_schema=EndTaskSchema)
def end_task():
    print("Task ended.")
    return {"status": "success", '__control__': 'end_task'}
