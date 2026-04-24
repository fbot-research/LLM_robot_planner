from pydantic import BaseModel, Field
from tool_registry import tool

class AskForHelpSchema(BaseModel):
    message: str = Field(..., description="Description of the issue or help needed.")

class SaySchema(BaseModel):
    message: str = Field(..., description="Message to say to the user.")

@tool(args_schema=AskForHelpSchema)
def ask_for_help(message: str):
    """Request human assistance for a specific issue or decision.
    
    Prompts the user for input, allowing human intervention
    when the agent encounters ambiguity, requires domain expertise, or needs
    clarification. The user's response is returned for the agent to process.
    
    Args:
        message: Description of the issue, decision, or information needed from the user.
    
    Returns:
        dict: Status with the original message and user's input response.
    """
    print(f"Requesting human assistance: \n{message} \n\nPlease provide your input: ")
    return {"status": "help_requested", "message": message, '__control__': 'done', 'input': input('>>> ')}

@tool(args_schema=SaySchema)
def say(message: str):
    """Output a message to communicate with the user.
    
    Displays a message to the user, but does not wait for a response.
    
    Args:
        message: The message text to output.
    
    Returns:
        dict: Status indicating successful message output.
    """
    print(f"LLM says: {message}")
    return {"status": "success", "message": message, '__control__': 'done'}
