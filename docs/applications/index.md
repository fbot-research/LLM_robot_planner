# Applications

This section describes practical applications and advantages of using an LLM-based planner instead of a traditional state machine. By operating at a higher level of abstraction, a language-model-driven planner can reason about goals, propose multi-step strategies, and adapt plans dynamically when unexpected conditions occur. This makes LLM planning particularly valuable for tasks that require flexible recovery behaviours, complex decision-making under uncertainty, or rapid adaptation to new scenarios.

Key advantages

- Flexibility and recovery: LLMs can suggest context-aware recovery steps when an action fails (e.g., alternative routes, sensor-backed checks), reducing the need to hand-code exhaustive failure states.
- Expressive plans: Plans are human-readable and can contain high-level rationale, making debugging and operator oversight easier.
- Rapid iteration: Updating behaviour often only requires changing prompt templates or tool descriptions, not extensive state-machine rewrites.
- Tool integration: The planner can orchestrate existing primitives (navigation, perception, manipulation) by emitting structured action descriptions that map to `tools/` functions.

Example application scenarios

- Field robotics and competitions (RoboCup): teams can benefit from on-the-fly strategy adjustments and robust recovery when plans diverge from expectations during matches.
- Inspection and maintenance: the planner can sequence perception and manipulation steps based on sensor feedback, re-planning when obstacles or anomalies are detected.
- Human-robot collaboration: natural-language directives from operators can be translated into executable action plans with clarifying questions or fallback behaviours when inputs are ambiguous.

Next steps

Provide concrete examples and benchmarks: recorded runs that compare an LLM-driven planner to equivalent state-machine implementations, include recovery scenarios, and measure success rate and time-to-completion. Also consider safety constraints and guarded tool wrappers to ensure any generated plan respects operational limits.