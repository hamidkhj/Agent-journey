from ollama import chat, ChatResponse
from helper import logger


def add(a: int, b: int) -> int:
  """Add two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The sum of the two numbers
  """

  print("add was called!!!!!!!!!!!!!!!!!!")
  return a + b


def multiply(a: int, b: int) -> int:
  """Multiply two numbers"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The product of the two numbers
  """

  print('Multiply was called!!!!!!!')
  return a * b


def divide(a: int, b: int) -> int:
  """Divide two numbers returning an integer"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The product of the two numbers
  """

  print('divide was called!!!!!!!')
  return a // b

def subtract(a: int, b: int) -> int:
  """Subtract two numbers (first number minus the second number)"""
  """
  Args:
    a: The first number
    b: The second number

  Returns:
    The product of the two numbers
  """

  print('subtract was called!!!!!!!')
  return a - b

available_functions = {
  'add': add,
  'multiply': multiply,
  'divide': divide,
  'subtract': subtract,
}

messages = [{'role': 'system', 'content': "You are an agent that always relies on tools available rather than your own knowledge"},
            {'role': 'user', 'content': 'What is (12324+54321)*(412 + 98765)/4523 - 67454?'}]
while True:
    response: ChatResponse = chat(
        model='gemma4:e4b',
        messages=messages,
        tools=[add, multiply, divide, subtract],
        think=True,
    )
    messages.append(response.message)
    print("Thinking: ", response.message.thinking)
    print("Content: ", response.message.content)
    if response.message.tool_calls:
        for tc in response.message.tool_calls:
            if tc.function.name in available_functions:
                print(f"Calling {tc.function.name} with arguments {tc.function.arguments}")
                result = available_functions[tc.function.name](**tc.function.arguments)
                print(f"Result: {result}")
                # add the tool result to the messages
                messages.append({'role': 'tool', 'tool_name': tc.function.name, 'content': str(result)})
    else:
        # end the loop when there are no more tool calls
        logger(messages=messages)
        break
  # continue the loop with the updated messages