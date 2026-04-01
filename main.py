from typing import Dict, Optional
import json
import logging
import ollama
import os
import importlib
from tool_registry import get_tools_schema, execute_tool
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

for filename in os.listdir("tools"):
    if filename.endswith(".py") and filename != "__init__.py":
        filepath = os.path.join("tools", filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

tools_for_llm = json.dumps(get_tools_schema(), indent=2)

system_prompt = f"""
{persona}

<rules>
{rules}
</rules>

<tools>
{tools_for_llm}
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

print(f"Sending prompt to {model}...")
# print("System Prompt:")
# print(system_prompt)
# print("\nUser Prompt:")
# print(built_msg)

finished = False

action_history = []

while not finished:

    resp = client.chat(
        model=model,
        format="json",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": built_msg},
        ],
    )

    plan = parse_ai_response(str(resp.message.content))


    if plan is not None:
        json.dumps(plan, indent=2)
        print("Parsed LLM response as JSON:")
        print(json.dumps(plan, indent=2))
        # print(f"\n{'-'*50}\n")
        # print(resp.message.content)
    else:
        print("Could not parse LLM response as JSON. Raw response:")
        print(resp.message.content)
        
        # TODO: ask the LLM to reformat
        
        pass

    if isinstance(plan, dict): 
        if "action" in plan:
            plan = [plan]  # Wrap single action in a list for uniform processing
        elif 'actions' in plan:
            plan = plan['actions']  # Extract actions list if wrapped in an "actions" field
        else:
            print("LLM response JSON does not contain 'action' or 'actions' field. Raw response:")
            print(resp.message.content)
            plan = []  # Set to empty list to avoid processing

    for step in plan:
        action_name = step.get("action")
        params = step.get("parameters", {})
        result = execute_tool(action_name, params)
        
        print(f"Result: {result}")
        action_history.append((action_name, params, result))

        system_prompt += f"""
        <command_history>
        {json.dumps(action_history, indent=2)}
        </command_history>
        """

        if result.get('__control__') == 'end_task':
            finished = True
            break
        elif result.get('__control__') == 'end_iteration':
            # Here you could also update the current_state based on the results of the command if needed
            break  # Break to send the updated context back to the LLM for the next iteration
        

        print(f"\n{'='*50}\n")

        

    with open("debug/raw_response.json", "w") as f:
        if hasattr(resp, "model_dump"):
            json.dump(resp.model_dump(), f, indent=2, default=str)
        elif isinstance(resp, dict):
            json.dump(resp, f, indent=2, default=str)
        else:
            f.write(str(resp))
