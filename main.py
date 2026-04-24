import json
import logging
import ollama
import os
import importlib
from tool_registry import get_tools_schema, execute_tool
from agent import parse_ai_response
from robot_state import get_state, update_state

logger = logging.getLogger(__name__)

# Default Ollama host used to create the client. Can be overridden in
# a production deployment via environment variables or a config file.
host = "http://localhost:11434"

model = "llama3.1:8b"

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

user_prompt = input("What task do you want the robot to perform? ")
finished = False
iteration_counter = 0
iteration_limit = 25

print(f"Task: {user_prompt}")
print(f"Sending prompt to {model}...")

action_history = []
thinking_supported = True


def stream_chat_response(messages: list[dict], use_thinking: bool):
    """Stream a chat response, optionally enabling model thinking output."""
    chat_kwargs = {
        "model": model,
        # "format": "json",
        "messages": messages,
        "stream": True,
    }
    if use_thinking:
        chat_kwargs["think"] = True

    resp = client.chat(**chat_kwargs)

    in_thinking = False
    thinking_text = ''
    response_text = ''

    for chunk in resp:
        thinking_chunk = getattr(chunk.message, "thinking", None)
        content_chunk = getattr(chunk.message, "content", None)

        if thinking_chunk and not in_thinking:
            in_thinking = True
            print('Thinking:\n', end='')

        if thinking_chunk:
            print(thinking_chunk, end='')
            thinking_text += thinking_chunk
        elif content_chunk:
            if in_thinking:
                print('\n\nAnswer:\n', end='')
                in_thinking = False
            print(content_chunk, end='')
            response_text += content_chunk

    return thinking_text, response_text

while not finished:

    update_state('places', {'Table A': {'x': 1.0, 'y': 2.0, 'z': 0.0}, 'Table B': {'x': -1.0, 'y': 3.0, 'z': 0.0}, 'Shelf': {'x': 2.0, 'y': -1.0, 'z': 1.0}})
    update_state('objects', {'cube': {'position': {'x': 1.0, 'y': 1.9, 'z': 0.1}}, 'ball': {'position': {'x': 1.0, 'y': 2.2, 'z': 0.1}}})
    # Get the latest state from robot_state module
    current_state = get_state()
    
    # Build the message with latest state for each iteration
    built_msg = f"""

{f'You have executed {iteration_counter} iterations so far. Your current state is:' if iteration_counter > 0 else ''}

<|current_state|>
{json.dumps(current_state, indent=2)}
<|current_state|>

The main task you need to accomplish is: {user_prompt}. Check if you haven't already accomplished part or all of it based on the current state and action history.
"""
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": built_msg},
    ]

    thinking = ''
    response = ''
    if thinking_supported:
        try:
            thinking, response = stream_chat_response(messages, use_thinking=True)
        except ollama.ResponseError as e:
            if "does not support thinking" in str(e):
                thinking_supported = False
                print(f"\nModel '{model}' does not support thinking. Continuing without thinking mode.\n")
                thinking, response = stream_chat_response(messages, use_thinking=False)
            else:
                raise
    else:
        thinking, response = stream_chat_response(messages, use_thinking=False)

    
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
        f.write("Streaming response consumed; content persisted in debug/response.txt and debug/thinking.txt")

    with open("debug/response.txt", 'w') as f:
        f.write(response)

    with open("debug/thinking.txt", 'w') as f:
        f.write(thinking)

print("Finished executing plan.")
print(action_history)
