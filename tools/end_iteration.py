tools =  {
        "name": "end_iteration",
        "description": "Indicates that the current iteration of the task is complete and the system must wait for environment feedback before proceeding.",
        "parameters": {},
    }

implementation = {
    "end_iteration": lambda: end_iteration()
    }

def end_iteration():
    #current base for and_iteration tool development
    print("End of iteration. Waiting for environment feedback...")