import asyncio
import json
from typing import Any, Callable, TypeAlias
from pydantic import BaseModel, Field

# Python 3.12 Type Aliases
Message: TypeAlias = dict[str, str]
ToolRegistry: TypeAlias = dict[str, Callable[..., Any]]

class AgentResponse(BaseModel):
    thought: str = Field(description="The reasoning behind the current action.")
    tool_name: str | None = Field(description="Name of the tool to invoke. 'finish' to end.")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool.")

class MaxIterationsExceeded(Exception):
    pass

async def execute_agent_loop(
    objective: str, 
    tools: ToolRegistry, 
    llm_client: Any, 
    max_steps: int = 15
) -> str:
    """
    Executes a stateful ReAct loop with hallucination mitigation.
    """
    system_prompt = (
        "You are an autonomous agent. You must reason about your objective, "
        "select a tool, and observe the output. To finish, use the tool 'finish'."
    )
    
    messages: list[Message] = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": objective}
    ]
    
    step = 0
    while step < max_steps:
        step += 1
        
        # 1. Generation (Assume llm_client handles structured JSON generation via schema)
        raw_response = await llm_client.generate(messages, response_format=AgentResponse)
        
        try:
            # 2. Parsing and Validation
            agent_action = AgentResponse.model_validate_json(raw_response)
        except json.JSONDecodeError:
            # Mitigation for Agentic Hallucination: The model forgot to output JSON
            error_msg = "SYSTEM ERROR: You did not output valid JSON. You must strictly follow the schema."
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({"role": "user", "content": error_msg})
            continue

        messages.append({
            "role": "assistant", 
            "content": f"Thought: {agent_action.thought}\nAction: {agent_action.tool_name}({agent_action.tool_args})"
        })

        # 3. Execution Routing via Python 3.12 Pattern Matching
        match agent_action.tool_name:
            case "finish":
                return str(agent_action.tool_args.get("final_answer", "No answer provided."))
            
            case None | "":
                # Mitigation for Agentic Hallucination: Model output JSON but no tool
                messages.append({
                    "role": "user", 
                    "content": "SYSTEM ERROR: No tool called. You must specify a tool_name or 'finish'."
                })
                continue
                
            case tool_name if tool_name in tools:
                try:
                    # 4. Observation Collection
                    tool_func = tools[tool_name]
                    # Utilizing async/await seamlessly if the tool is an async coroutine
                    if asyncio.iscoroutinefunction(tool_func):
                        observation = await tool_func(**agent_action.tool_args)
                    else:
                        observation = tool_func(**agent_action.tool_args)
                except Exception as e:
                    observation = f"TOOL FATAL ERROR: {type(e).__name__}: {str(e)}"
            
            case _:
                observation = f"TOOL ERROR: Tool '{agent_action.tool_name}' does not exist."

        # 5. State Mutation
        messages.append({"role": "user", "content": f"Observation: {observation}"})

    raise MaxIterationsExceeded(f"Agent failed to resolve objective within {max_steps} steps.")