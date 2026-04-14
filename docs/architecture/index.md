# Architecture

This document expands the high-level architecture introduced on the main page and describes how the repository is organized, how the prompt/LLM/execution loop is structured, and how each module shown in the project diagram participates in that loop.

Repository layout (high level)

- **Core orchestrator:** `agent.py`, `main.py` and `tool_registry.py` implement prompt assembly, model invocation, response parsing and dispatch to tools.

- **Configuration & persona:** `settings.py` and the `settings/` folder contain rules, personas, tool descriptions and examples used to build the system prompt.

- **Tools:** the `tools/` package contains the Python functions that implement actionable primitives (many are ROS2 wrappers like motion, navigation, gripper control, perception helpers).

- **Documentation & examples:** `docs/` holds project documentation, diagrams and tutorials; `applications/`, `tutorial/` and `tests/` provide example usage, hands-on guides and automated tests.


### Project diagram

![image](../_static/function_diagram.svg)



- **Available tools:** registry of callable tools (name, parameters, description) that the orchestrator can map actions to. Each entry usually points to a function in `tools/`.
- **System base prompt:** the static part of the system prompt (rules, persona, formatting constraints and examples) that guides the LLM's behaviour.
- **System prompt:** combination of the base prompt and the available tools' metadata, presented as the system message to the model.
- **User informed task:** the task or instruction supplied by the user describing what should be achieved.
- **Context:** runtime contextual information (sensor readings, map state, previous actions, execution results) that augments the user task.
- **User prompt:** the prompt built from the user task plus context, often provided as a user message in the LLM conversation.
- **Input prompt:** the final prompt given to the model, typically composed by merging `system prompt` and `user prompt` into the format expected by the LLM client.
- **Local LLM:** model endpoint used for inference (the project uses a local client such as Ollama; can be swapped if needed).
- **JSON output:** the LLM's structured response — expected to be valid JSON describing a sequence of actions with tool names and arguments.
- **Execution:** the interpreter that parses the JSON and invokes corresponding Python tools (wrappers for ROS2 commands, or pure-Python helpers). It handles success/failure reporting and may update the context.
- **End condition:** the loop control that determines whether the task is complete (e.g., goal reached, explicit stop action, or unrecoverable failure).

### Example usage flows

- Simple single-step command
	1. User issues a straightforward request (e.g., "move the robot to waypoint A").
 2. The system builds the `user prompt` (task + minimal context) and merges it with the `system prompt`.
 3. The `input prompt` is sent to the local LLM, which returns JSON with an action like `{ "tool": "navigate_to", "args": {"point": "A"} }`.
 4. The execution layer calls the `navigate_to` tool in `tools/`, monitors progress, and reports success or failure back to the context.

- Iterative planning and execution (multi-step)
	1. User requests a multi-step job (e.g., "inspect points A, B, and C and report any obstacles").
 2. The orchestrator includes richer context (map fragments, previous observations) in the `user prompt`.
 3. LLM returns a JSON plan with several ordered actions (perception calls, navigation calls, gripper manipulations).
 4. The execution layer runs actions sequentially; after each action it appends results to the context and may re-invoke the LLM with updated context if the plan requires re-evaluation.
 5. The loop continues until the plan completes or the `end condition` is triggered (success or stop).

### Notes and extension points

- Tools should validate inputs and return structured results so the context remains consistent.
- The prompt templates in `settings/` are the recommended place to tune behaviour (safety constraints, verbosity, retry policies).
- The LLM client is pluggable; replace the inference call in the orchestrator to integrate other local or remote models.

For further, module-level details and code pointers, see the specific tool implementations under `tools/` and the orchestrator entry points `agent.py` and `main.py`.