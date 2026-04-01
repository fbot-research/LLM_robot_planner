# examples.md

<example_1>
User: "Pick the red ball"
Current State indicates red ball is at x:0.5, y:0.5, z:0.0.
Response:
[
    {
        "action": "navigate_to",
        "parameters": {"x": 0.5, "y": 0.5, "z": 0.0, "orientation": [0.0, 0.0, 0.0, 1.0]}
    },
    {
        "action": "move_arm",
        "parameters": {"x": 1.0, "y": 1.0, "z": 0.05}
    },
    {
        "action": "close_gripper",
        "parameters": {}
    },
    {
        "action": "end_task",
        "parameters": {}
    }
]
</example_1>

<example_2>
User: "Pick the pen and place it on the table"
Current State does NOT show a pen or a table.
Response:
[
    {
        "action": "call_ros",
        "parameters": {"command": "topic list"}
    },
    {
        "action": "end_iteration",
        "parameters": {}
    }
]
The command returns "
/feedback
/parameter_events
/rosout
/arena_poses
/detected_objects
".
You receive this context, previsously executed commands, and answer:

[
    {
        "action": "call_ros",
        "parameters": {"command": "topic echo /arena_poses --once"}
    },
    {
        "action": "call_ros",
        "parameters": {"command": "topic echo /detected_objects --once"}
    }
    {
        "action": "end_iteration",
        "parameters": {}
    }
]
The commands returns two YAML formatted responses the position of the table and the pen, respectively:
/arena_poses:
- id: "table1"
    type: "table"
    position:
        x: 1.0
        y: 0.0
        z: 0.0
-----------------------
\n
/detected_objects:
- id: "object1"
    type: "pen"
    position:
        x: 0.5
        y: 0.5
        z: 0.0
-----------------------

You receive this context, previsously executed commands, and answer:
[
    {
        "action": "navigate_to",
        "parameters": {"x": 0.4, "y": 0.4, "z": 0.0, "orientation_q": [0.0, 0.0, 0.0, 1.0]}
    },
    {
        "action": "move_arm",
        "parameters": {"x": 0.5, "y": 0.5, "z": 0.05}
    },
    {
        "action": "close_gripper",
        "parameters": {}
    },
    {
        "action": "move_arm",
        "parameters": {"x": 0.0, "y": 0.0, "z": 0.05}
    },
    {
        "action": "navigate_to",
        "parameters": {"x": 1.0, "y": 0.0, "z": 0.0, "orientation_q": [0.0, 0.0, 0.0, 1.0]}
    },
    {
        "action": "move_arm",
        "parameters": {"x": 0.2, "y": 0.2, "z": 0.0}
    },
    {
        "action": "open_gripper",
        "parameters": {}
    },
    {
        "action": "end_task",
        "parameters": {}
    }
]

</example_2>