tools = {
        "name": "ask_for_help",
        "description": "Ask for human assistance if the task is too complex, impossible, or if context is missing.",
        "parameters": {
            "message": "string, describing the issue or the help needed."
        },
    }

implementation = {"ask_for_help": lambda message: input(f"Requesting human assistance: \n{message} \n\nPlease provide your input: ")}