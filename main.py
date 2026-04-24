from openai import OpenAI

# 1. Initialize the client pointing to your local Ollama server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama" # The API key is required by the library, but Ollama ignores it
)

# 2. Define your system and user prompts
messages = [
    {
        "role": "system",
        "content": "You are a helpful, logical AI assistant. Answer concisely."
    },
    {
        "role": "user",
        "content": "What are the primary benefits of running a local LLM for agentic workflows?"
    }
]

print("Thinking...\n")

# 3. Call the model
try:

    chat_completion = client.chat.completions.create(
        messages=[
            {
                'role': 'user',
                'content': 'Say this is a test',
            }
        ],
        model='llama3.1:8b',
    )
    print(chat_completion.choices[0].message.content)

except Exception as e:
    print(f"An error occurred: {e}")

