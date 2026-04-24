import json
from typing import Any, Callable
from pydantic import BaseModel, Field

# 1. The Reusable Schema
class AgentResponse(BaseModel):
    thought: str = Field(description="The reasoning behind the current action.")
    tool_name: str | None = Field(description="Name of the tool to invoke. 'finish' to end.")
    tool_args: dict[str, Any] = Field(default_factory=dict, description="Arguments for the tool.")

# 2. The Reusable Loop
async def execute_agent_loop(
    objective: str, 
    tools: dict[str, Callable], 
    client: Any, 
    model_name: str,
    system_prompt: str,
    max_steps: int = 25
) -> str:
    
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": objective}
    ]
    
    step = 0
    while step < max_steps:
        step += 1
        
        # response = await client.chat.completions.create(
        #     model=model_name,
        #     messages=messages,
        #     response_format={"type": "json_object"},
        #     temperature=0.1
        # )
        

        response = await client.chat.completions.create(
        messages=messages,
        model=model_name,
        response_format={"type": "json_object"},
        temperature=0.1
        )

        raw_response = response.choices[0].message.content
        print(raw_response)
        
        try:
            parsed_json = json.loads(raw_response)
            agent_action = AgentResponse(**parsed_json)
        except Exception as e:
            messages.append({"role": "assistant", "content": raw_response})
            messages.append({"role": "user", "content": "SYSTEM ERROR: Invalid JSON format. Fix formatting."})
            continue

        messages.append({"role": "assistant", "content": raw_response})

        match agent_action.tool_name:
            case "finish":
                return str(agent_action.tool_args.get("final_answer", "No answer provided."))
            
            case tool_name if tool_name in tools:
                try:
                    tool_func = tools[tool_name]
                    observation = tool_func(**agent_action.tool_args)
                except Exception as e:
                    observation = f"Error executing tool: {e}"
            
            case _:
                observation = f"Tool '{agent_action.tool_name}' does not exist."

        messages.append({"role": "user", "content": f"Observation: {observation}"})

    return "Agent failed to resolve objective within step limit."