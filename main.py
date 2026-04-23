import json
import logging
import ollama
import os
import importlib
from tool_registry import get_tools_schema, execute_tool
from agent import parse_ai_response

logger = logging.getLogger(__name__)

# Default Ollama host used to create the client. Can be overridden in
# a production deployment via environment variables or a config file.
host = "http://localhost:11434"

model = "gemma4:e4b"

client = ollama.Client(host=host)

with open("settings/prompt.md", "r") as f:
    prompt = f.read()

for filename in os.listdir("tools"):
    if filename.endswith(".py") and filename != "__init__.py":
        filepath = os.path.join("tools", filename)
        spec = importlib.util.spec_from_file_location(filename[:-3], filepath)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

tools_for_llm = json.dumps(get_tools_schema(), indent=2)

system_prompt = f"""{prompt}"""

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
        "places": [
            {"id": "place1", "type": "table", "position": {"x": 2.0, "y": 2.0, "z": 0.0}}
        ]
    }
}

user_prompt = input("What task do you want the robot to perform? ")
finished = False
iteration_counter = 0
iteration_limit = 25

built_msg = f"""

{f'You have executed {iteration_counter} iterations so far. Your current state is:' if iteration_counter > 0 else ''}

<|current_state|>
{json.dumps(current_state, indent=2)}
<|current_state|>

<|user_request|>
{user_prompt}
<|user_request|>
"""

# print(built_msg)
print(f"Task: {user_prompt}")
print(f"Sending prompt to {model}...")
# print("System Prompt:")
# print(system_prompt)
# print("\nUser Prompt:")
# print(built_msg)


action_history = []

while not finished:

    resp = client.chat(
        model=model,
        format="json",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": built_msg},
        ],
        think=True,
        stream=True,
    )

    in_thinking = False

    thinking = ''
    response = ''
    
    for chunk in resp:
        if chunk.message.thinking and not in_thinking:
            in_thinking = True
            print('Thinking:\n', end='')

        if chunk.message.thinking:
            print(chunk.message.thinking, end='')
            thinking += chunk.message.thinking
        elif chunk.message.content:
            if in_thinking:
                print('\n\nAnswer:\n', end='')
                in_thinking = False
            print(chunk.message.content, end='')
            response += chunk.message.content

    
    plan = parse_ai_response(response)


    if plan is not None:
        json.dumps(plan, indent=2)
        print("Parsed LLM response as JSON:")
        print(json.dumps(plan, indent=2))
        # print(f"\n{'-'*50}\n")
        # print(final_resp.message.content)
    else:
        print("Could not parse LLM response as JSON. Raw response:")
        print(response)
        
        # TODO: ask the LLM to reformat
        
        pass

    if isinstance(plan, dict): 
        if "action" in plan:
            plan = [plan]  # Wrap single action in a list for uniform processing
        elif 'actions' in plan:
            plan = plan['actions']  # Extract actions list if wrapped in an "actions" field
        else:
            print("LLM response JSON does not contain 'action' or 'actions' field. Raw response:")
            print(response)
            plan = []  # Set to empty list to avoid processing

    for step in plan:
        iteration_counter += 1
        action_name = step.get("action")
        params = step.get("parameters", {})
        result = execute_tool(action_name, params)
        
        print(f'Executing action: {action_name}({params})')

        print(f"Result: {result}")
        action_history.append((action_name, params, result))

        system_prompt += f"""
        <|command_history|>
        {json.dumps(action_history, indent=2)}
        <|command_history|>
        """

        # TODO: add a try and ask llm to fix if something goes wrong

        if result.get('__control__') == 'end_task':
            finished = True
            break
        elif result.get('__control__') == 'end_iteration':
            # Here you could also update the current_state based on the results of the command if needed
            break  # Break to send the updated context back to the LLM for the next iteration
        
        print(f"\n{'-'*50}\n")
        print(f"Iteration {iteration_counter} completed. Sending updated context back to LLM for next iteration...")
        print(f"\n{'='*50}\n")

    if iteration_counter >= iteration_limit:
        print("Iteration limit reached. Ending execution.")
        finished = True

    with open("debug/raw_response.json", "w") as f:
        if hasattr(resp, "model_dump"):
            json.dump(resp.model_dump(), f, indent=2, default=str)
        elif isinstance(resp, dict):
            json.dump(resp, f, indent=2, default=str)
        else:
            f.write(str(resp))

    with open("debug/response.txt", 'w') as f:
        f.write(response)

    with open("debug/thinking.txt", 'w') as f:
        f.write(thinking)

print("Finished executing plan.")
