tools = {
        "name": "end_task",
        "description": "Indicates that the entire task is complete and no further actions are needed.",
        "parameters": {},
    }

implementation = {
    "end_task": lambda: end_task(),
}

def end_task():
    #This function indicates that the entire task is complete and no further actions are needed.
    print("Task completed. No further actions are needed.")