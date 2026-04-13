from pydantic import BaseModel, Field
from tool_registry import tool

class AskForHelpSchema(BaseModel):
    message: str = Field(..., description="Description of the issue or help needed.")

class SaySchema(BaseModel):
    message: str = Field(..., description="Message to say to the user.")

@tool(args_schema=AskForHelpSchema)
def ask_for_help(message: str):
    print(f"Requesting human assistance: \n{message} \n\nPlease provide your input: ")
    return {"status": "help_requested", "message": message, '__control__': 'done', 'input': input('>>> ')}

@tool(args_schema=SaySchema)
def say(message: str):
    print(f"LLM says: {message}")
    return {"status": "success", "message": message, '__control__': 'done'}