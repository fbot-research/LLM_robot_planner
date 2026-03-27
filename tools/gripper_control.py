tools = [{
        "name": "close_gripper",
        "description": "Close the gripper to grip an object at the current position.",
        "parameters": {},
    }, 
     {
        "name": "open_gripper",
        "description": "Open the gripper to release any currently gripped object at the current position.",
        "parameters": {},
    },]

implementation = {
    "close_gripper": lambda: open_gripper(),
    "open_gripper": lambda: close_gripper(),
}

def open_gripper():
    print("Gripper opened.")

def close_gripper():    
    print("Gripper closed.")