from pydantic import BaseModel, Field
from tool_registry import tool

class AskForHelpSchema(BaseModel):
    message: str = Field(..., description="Description of the issue or help needed.")

@tool(args_schema=AskForHelpSchema)
def ask_for_help(message: str):
    print(f"Requesting human assistance: \n{message} \n\nPlease provide your input: ")
    return {"status": "help_requested", "message": message, '__control__': 'ask_for_help', 'input': input('>>> ')}