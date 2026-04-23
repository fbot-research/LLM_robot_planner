from pydantic import BaseModel, Field
from tool_registry import tool

class EndIterationSchema(BaseModel):
    pass  # No parameters needed for this simple command

@tool(args_schema=EndIterationSchema)
def end_iteration():
    """Mark the end of the current iteration.
    
    Signals completion of the current iteration in a planning or reasoning loop.
    This allows the agent to checkpoint progress and prepare for the next
    iteration of task planning or execution.
    
    Returns:
        dict: Status with control directive to end iteration.
    """
    print("Iteration ended.")
    return {"status": "success", '__control__': 'end_iteration'}