from pydantic import BaseModel, Field
from tool_registry import tool

class EndIterationSchema(BaseModel):
    pass  # No parameters needed for this simple command

@tool(args_schema=EndIterationSchema)
def end_iteration():
    print("Iteration ended.")
    return {"status": "success", '__control__': 'end_iteration'}