# LLM Robot Planner

## Description

LLM Robot Planner is an orchestrator for planning and executing robotic actions controlled by an LLM. It builds a structured prompt (rules, persona, tools, and examples), sends it to the model through the `ollama` client, interprets the LLM response as a sequence of actions in JSON, and executes the actions mapped to Python functions (tools) — many of which are wrappers for ROS 2 commands.

## Main features

* Structured prompt with: persona, operating rules, tool descriptions, and examples.
* Integration with the `ollama` client for local/hosted inference.
* Robust JSON extraction from LLM responses (heuristics in `agent.py`).
* Automatic registration of available tools (decorator in `tool_registry.py`) and parameter validation via Pydantic.
* Set of tools for navigation, robot manipulation, and ROS calls: `tools/`.
* Generation of debugging artifacts (`debug/response.txt`, `debug/raw_response.json`) during execution.

## Requirements

* Python 3.8+
* Main dependency: `ollama` (see `requirements.txt`).
* (Optional, but required for ROS functionality) ROS 2 installed and accessible in the `PATH`.

## Quick installation

1. Create and activate a Python virtual environment.
2. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

3. Adjust the Ollama client host if necessary by editing the `host` variable in [main.py](main.py).

## Basic usage

1. Adjust `user_prompt` and, if desired, `current_state` in [main.py](main.py).
2. Run:

```bash
python3 main.py
```

During execution, the orchestrator sends the prompt to the LLM, attempts to parse the response using `parse_ai_response`, and, for each received action, calls `execute_tool` in `tool_registry.py`.

## Security and production recommendations

* Do not execute physical commands on the robot without additional human validation.
* The project uses `subprocess.run(..., shell=True)` in some places (`call_ros`, `tools/ros_tools.py`) — replace these with ROS 2 clients and bindings (`rclpy`) for production.
* Always validate and sanitize inputs/outputs; using Pydantic reduces parameter formatting errors.

## Project structure and file descriptions

* **`main.py`**: Main orchestrator. Builds the `system_prompt` (combines `settings/persona.md`, `settings/rules.md`, tools via `get_tools_schema()`, and `settings/examples.md`), sends the messages to the `ollama.Client`, receives the response, uses `parse_ai_response` to obtain JSON, and then executes each step with `execute_tool`. It also contains `call_ros()` (a simple wrapper for the `ros2` CLI) and generates debug files in `debug/`.
* **`agent.py`**: Functions for parsing LLM responses. Implements `parse_ai_response(response_text)` with several heuristics (attempts to parse directly, searches for `json` code blocks, and looks for substrings that resemble JSON). Returns `None` if parsing fails.
* **`tool_registry.py`**: Tool registration system. Provides the `@tool(args_schema=...)` decorator, which registers functions as tools, builds metadata (name, description, JSON Schema via Pydantic), and stores the Pydantic model for parameter validation. `get_tools_schema()` returns the list of schemas for injection into the LLM prompt. `execute_tool(action_name, parameters)` validates and executes the tool.
* **`settings/`**: Content used to build prompts:

  * [settings/persona.md](settings/persona.md): Agent persona (e.g., `"You are AutoBot AI..."`).
  * [settings/rules.md](settings/rules.md): Rules that the LLM must follow (mandatory JSON response format, use of `call_ros` when necessary, use of `end_task`/`end_iteration`, etc.).
  * [settings/examples.md](settings/examples.md): Examples of prompts and responses (useful for few-shot learning).
* **`requirements.txt`**: Minimal dependency list (e.g., `ollama`).
* **`tools/`**: Set of tools registered through `tool_registry.tool`. Each module defines a Pydantic schema and functions annotated with `@tool(...)`:

  * [tools/ask_for_help.py](tools/ask_for_help.py): Requests human intervention; prints a message and reads input from the operator.
  * [tools/end_iteration.py](tools/end_iteration.py): Marks the end of an iteration and returns `{'__control__': 'end_iteration'}`.
  * [tools/end_task.py](tools/end_task.py): Marks the end of the task (`{'__control__': 'end_task'}`).
  * [tools/gripper_control.py](tools/gripper_control.py): Functions `open_gripper()` and `close_gripper()` (simple stubs that print a message and return success).
  * [tools/move_arm.py](tools/move_arm.py): `move_arm(x,y,z,orientation)` — stub that prints the destination; expected to be replaced with a call to a real ROS action.
  * [tools/navigate_to.py](tools/navigate_to.py): `navigate_to(x,y,z,orientation)` — navigation stub.
  * [tools/ros_tools.py](tools/ros_tools.py): Generic tools for listing topics, `echo`, publishing messages, and calling services via the `ros2` CLI.

## Other directories

* **`docs/`**: Sphinx/ReadTheDocs documentation already included (pages in `docs/` and build in `docs/_build/html`). Use `make html` inside `docs/` to generate the static version.
* **`debug/`**: (created at runtime) Contains `raw_response.json` and `response.txt` with the LLM response for analysis.

## How tools are declared and validated

The `@tool(args_schema=...)` decorator in `tool_registry.py` receives a Pydantic model describing the parameters. This model automatically generates a JSON Schema included in the LLM prompt — helping the model produce responses in the correct format. At runtime, `execute_tool` validates the payload from the LLM against the Pydantic model; validation failures are returned as readable error messages.

## Example workflow

1. `main.py` builds the `system_prompt` with the persona, rules, tools, and examples.
2. Sends the prompt via `ollama.Client.chat(...)`.
3. Receives the LLM text; `parse_ai_response` attempts to extract the JSON.
4. For each action in the JSON array: calls `execute_tool(action, parameters)`.
5. Tools can return a `__control__` field to control the loop (`end_iteration`, `end_task`, etc.).

## Contributing

* To add a new tool, create a new file in `tools/` or edit an existing one. Declare a Pydantic `BaseModel` with the expected parameters and add `@tool(args_schema=YourModel)` above the implemented function.
* Open issues to discuss major changes. Tests and examples are welcome.

## Examples and debugging

* Input/output examples are available in [settings/examples.md](settings/examples.md).
* During execution, `main.py` writes `debug/response.txt` and `debug/raw_response.json` to inspect the raw LLM response.

## License

Add the desired license (for example, MIT) to the repository.

## Contact

Open an issue in the repository or submit a PR with improvements.
