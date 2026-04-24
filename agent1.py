import asyncio
from openai import AsyncOpenAI

# 1. Import your custom engine
from base_engine import execute_agent_loop

# 2. Define tools for THIS specific project
def add(a: float, b: float) -> float:
    return a + b

def multiply(a: float, b: float) -> float:
    return a * b

my_tools = {
    "add": add,
    "multiply": multiply
}


system_instructions = """You are a math agent. 
Available tools:
1. add(a, b)
2. multiply(a, b)
3. finish(final_answer)

You MUST respond ONLY with valid JSON containing 'thought', 'tool_name', and 'tool_args'."""

# 4. Run the application
async def main():
    problem = "What is 5 plus 10, multiplied by 4?"
    
    result = await execute_agent_loop(
        objective=problem,
        tools=my_tools,
        model_name="llama3.1:8b",
        system_prompt=system_instructions
    )
    
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(main())