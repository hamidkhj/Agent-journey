def logger(messages=""):
    with open('log.txt', 'w', encoding='utf-8') as f:
            f.write("=== AGENT CONVERSATION LOG ===\n")
            f.write("=" * 30 + "\n\n")
            
            for msg in messages:
                # Handle standard dictionaries (system, user, tool results)
                if isinstance(msg, dict):
                    role = msg.get('role', 'UNKNOWN').upper()
                    f.write(f"[{role}]\n")
                    
                    if role == 'TOOL':
                        f.write(f"Function: {msg.get('tool_name')}\n")
                        f.write(f"Result: {msg.get('content')}\n")
                    else:
                        f.write(f"{msg.get('content')}\n")
                
                # Handle Ollama message objects (assistant responses)
                else:
                    role = getattr(msg, 'role', 'UNKNOWN').upper()
                    f.write(f"[{role}]\n")
                    
                    # Log the thinking process if it exists
                    thinking = getattr(msg, 'thinking', '')
                    if thinking:
                        f.write(f"--- Thinking ---\n{thinking.strip()}\n----------------\n")
                    
                    # Log standard text content
                    content = getattr(msg, 'content', '')
                    if content:
                        f.write(f"{content.strip()}\n")
                    
                    # Log tool calls explicitly
                    tool_calls = getattr(msg, 'tool_calls', [])
                    if tool_calls:
                        for tc in tool_calls:
                            f.write(f">> Action: Call '{tc.function.name}'\n")
                            f.write(f">> Arguments: {tc.function.arguments}\n")
                
                # Separator between messages
                f.write("\n" + "-" * 40 + "\n\n")