from claude_agent.anthropic_client import chat, add_user_message,  add_assistant_message
from claude_agent.tools.registry import TOOLS, run_tools
import json

def run_conversations(messages):
    while True:
        response = chat(messages, tools=TOOLS)
        tool_use = [b for b in response.content if b.type == "tool_use"]
        print(f"\n--- API Call: stop_response={response.stop_reason}, {len(tool_use)} tool_use block(s) ---")
        
        # preserve continious history
        add_assistant_message(messages, response.content)
        
        # Claude done: claude stop reason !=  tool_use
        if response.stop_reason != "tool_use":
            return "".join(b.text for b in response.content if b.type == "text")
         
        # caude needs tool calling
        tools_results = [] 
        for block in response.content:
            if block.type == "tool_use":
                print(f"tool calling {block.name}({block.input})")
                try:
                    result = run_tools(block.name, block.input)
                    tools_results.append(
                        {
                        "type" : "tool_result", 
                        "tool_use_id" : block.id,
                        "content" : json.dumps(result)
                        }
                    )
                except Exception as e:  
                    tools_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": f"Error: {e}",
                        "is_error": True,          # tells Claude the call failed
                    })
            
        # send result back to claude for complete final answer
        messages.append(
            {
            "role" : "user",
            "content" : tools_results
            }
        )
        
    
if __name__ == "__main__":
    messages = []
    while True:
        text = input("You: ")
        if text is None or text.strip().lower() in {"exit", "quit"}:
            break
        add_user_message(messages, text)
        assistant_reply = run_conversations(messages)
        print("Assistant:", assistant_reply)