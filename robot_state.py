"""
Shared robot state manager.
Tools import and modify this state directly after successful execution.
Provides parametric state updates to flexibly add new fields and information.
"""

robot_state = {
    "current_position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "current_orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "arm_position": {"x": 0.0, "y": 0.0, "z": 0.5},
    "arm_orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "gripped_object": None,
    "gripper_state": "open",
}

def update_state(key: str, value, nested_key: str = None):
    """
    Parametrically update robot state.
    
    Args:
        key: Top-level state key to update (e.g., 'gripper_state', 'current_position', 'detections')
        value: Value to set or update
        nested_key: Optional nested key for dict values (e.g., 'x' for current_position.x)
    
    Examples:
        update_state('gripper_state', 'closed')
        update_state('current_position', 0.5, 'x')
        update_state('current_orientation', [0.0, 0.0, 0.7071, 0.7071])
        update_state('detections', [{'type': 'cube', 'position': {'x': 1.0}}])
        update_state('arm_position', {'x': 1.5, 'y': 2.0, 'z': 0.8})
    """
    if key not in robot_state and nested_key is None:
        # Initialize new top-level key if it doesn't exist
        robot_state[key] = value
    elif nested_key is not None:
        # Update nested value within a dict
        if key not in robot_state:
            robot_state[key] = {}
        if isinstance(robot_state[key], dict):
            robot_state[key][nested_key] = value
        else:
            raise ValueError(f"Cannot set nested key '{nested_key}' on non-dict value at '{key}'")
    else:
        # Update top-level value
        robot_state[key] = value

def get_state():
    """Get current robot state."""
    return robot_state.copy() if isinstance(robot_state, dict) else robot_state
