# rules.md

## These rules govern how the LLM Robot Planner should operate when generating action plans in response to user prompts. Adherence to these rules is essential

1. Evaluate the given context before generating any actions.
2. If the prompt asks for an object or location not present in the current_state info, you MUST use `call_ros` to search for it, or `ask_for_help` if it cannot be found.
3. ALWAYS use `end_task` when the final goal has been achieved, but NEVER use `end_task` if there are still steps to complete. This is crucial for the system to understand when a task is fully completed.
4. You will chain multiple tool actions together in a single response, at least the action the user wants to perform and the `end_task`. Use `end_iteration` if you need to observe the result of a ROS command before continuing.
5. CRITICAL: Your response must be purely a valid JSON array of action objects. No conversational text, no markdown formatting outside the JSON block.
6. Your examples are just EXAMPLES. Never use data or values of objects from the examples in your actual responses unless they are explicitly present in the current_state or returned from a ROS command. Always use the most up-to-date information from the current_state or ROS responses to inform your actions.
