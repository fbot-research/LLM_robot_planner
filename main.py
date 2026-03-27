from typing import Dict, Optional
import json
import logging
import ollama
# from agent import parse_ai_response

logger = logging.getLogger(__name__)

# Default Ollama host used to create the client. Can be overridden in
# a production deployment via environment variables or a config file.
host = "http://localhost:11434"

# model = "granite4:3b"
model = "llama3.1:8b"
# model = "gemma3:4b"

client = ollama.Client(host=host)




def call_ros(command: str) -> str:
    """Execute a ROS 2 CLI command and return its standard output.

    This is a thin wrapper around ``subprocess.run`` intended for use in
    prototyping and tests. It invokes the ``ros2`` CLI; in production code
    consider using a ROS client library instead of shelling out.

    :param command: The ROS 2 CLI command arguments (e.g. ``"topic list"``).
    :return: The captured stdout from the command, or an error message if the
             call failed.
    """
    import subprocess

    try:
        result = subprocess.run(
            f"ros2 {command}", capture_output=True, text=True, shell=True
        )
        print(result.stdout)
        return result.stdout
    except Exception as e:
        logger.error(f"Error calling ROS command: {e}")
        print(f"Error calling ROS command: {e}")
        return f"Error calling ROS command: {e}"

# Import tools, examples, persona and rules from separate files to keep this main script clean


with open("settings/rules.md", "r") as f:
    rules = f.read()

with open("settings/examples.md", "r") as f:
    examples = f.read()

with open("settings/persona.md", "r") as f:
    persona = f.read()

import tools

for tool in tools:
    print(f"Loaded tool: {tool['name']} - {tool['description']} with parameters {tool['parameters']}")


system_prompt = f"""
{persona}

<rules>
{rules}
</rules>

<tools>
{tools}
</tools>

<examples>
{examples}
</examples>

RESPONSE FORMAT:
You MUST respond with a single valid JSON array containing the sequence of actions. Do not wrap it in markdown code blocks if possible, just output the raw JSON.
"""

# TODO: get the current state from ROS topics instead of hardcoding it here. This is just an example.
current_state = {
    "current_position": {"x": 0.0, "y": 0.0, "z": 0.0},
    "current_orientation": {"x": 0.0, "y": 0.0, "z": 0.0, "w": 1.0},
    "gripped_object": None,
    "gripper_state": "open",
    "environment": {
        "objects": [
            {"id": "object1", "type": "box", "position": {"x": 1.0, "y": 1.0, "z": 0.0}}
        ],
    }
}

user_prompt = "Pick up the box and move it to the left side of the table."

built_msg = f"""

<current_state>
{json.dumps(current_state, indent=2)}
</current_state>

<user_request>
{user_prompt}
</user_request>
"""

# print(built_msg)

print("Sending prompt to LLM...")
print("System Prompt:")
print(system_prompt)
print("\nUser Prompt:")
print(built_msg)

resp = client.chat(
    model=model,
    # format="json",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": built_msg},
    ],
)

# print(f"{'\n'*5}LLM Response:")
parsed_resp = parse_ai_response(str(resp.message.content))

if parsed_resp is not None:
    json.dumps(parsed_resp, indent=2)
    print("Parsed LLM response as JSON:")
    print(json.dumps(parsed_resp, indent=2))
    print(f"\n{'-'*50}\n")
    print(resp.message.content)
else:
    print("Could not parse LLM response as JSON. Raw response:")
    print(resp.message.content)
    pass

# for action in parsed_resp:
#     try:
#         assert (
#             "action" in action
#         ), "Each item in the response must have an 'action' key"
#         # print(action)
#         print(
#             f"Executing action: {action['action']}"
#             + (
#                 f"with parameters: {action['parameters']}"
#                 if hasattr(action, "parameters")
#                 else ""
#             )
#         ) 
#         if action["action"] == "call_ros":
#             command = action["parameters"]["command"]
#             ros_response = call_ros(command)
#             print(f"ROS response: {ros_response}")

#     except AssertionError as ae:
#         logger.error(f"Invalid action format: {action} - {ae}")
#         print(f"Invalid action format: {action} - {ae}")
#         continue

#     except Exception as e:
#         logger.error(f"Error executing action {action}: {e}")
#         print(f"Error executing action {action}: {e}")
#         continue

with open("response.json", "w") as f:
    if hasattr(resp, "model_dump"):
        json.dump(resp.model_dump(), f, indent=2, ensure_ascii=False)
    elif isinstance(resp, dict):
        json.dump(resp, f, indent=2, ensure_ascii=False, default=str)
    else:
        f.write(str(resp))
