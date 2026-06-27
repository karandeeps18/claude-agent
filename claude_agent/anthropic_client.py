# chat function to talk to anthropic 
from dotenv import load_dotenv
from anthropic import Anthropic
from rich import print_json


load_dotenv()

client = Anthropic()
model = "claude-sonnet-4-6"
messages = []

# helper function 
def add_user_message(messages, text):
    user_message = {"role": "user", "content": text}
    messages.append(user_message)
    
def add_assistant_message(messages, text):
    assistant_message = {"role": "assistant", "content": text}
    messages.append(assistant_message)
    
# chat 
def chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None):
    params = {
        "model" : model, 
        "max_tokens" : 3000, 
        "messages" : messages, 
        "temperature" : temperature, 
        "stop_sequences" : stop_sequences,
    }
    
    # optional params 
    if system is not None:
        params["system"] = system
    if tools is not None:
        params["tools"] = tools
        
    # response 
    return client.messages.create(**params)

if __name__ == "__main__":
    text = """ what is current time """
    messages = []
    add_user_message(messages, text)
    response = chat(messages)
    print_json(response.model_dump_json()) 
