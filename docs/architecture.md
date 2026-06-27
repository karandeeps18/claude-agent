# Architecture

The agent has three layers: a thin **SDK wrapper**, a **tool registry**, and the
**agent loop** that ties them together.

```
                 ┌──────────────────────────────────────────┐
                 │            run_conversations()             │
                 │                 (the loop)                 │
                 └──────────────────────────────────────────┘
   User text ──▶ add_user_message ──▶ chat(messages, tools=TOOLS) ──▶ Claude
                                                  │
                          stop_reason == "tool_use"?
                              │                     │
                            yes                    no
                              │                     │
              run_tools(name, input) for       return final
              every tool_use block             text answer
                              │
              append tool_result(s) ──▶ loop back to chat()
```

## 1. The SDK wrapper — `anthropic_client.py`

A minimal layer over the Anthropic SDK:

- `chat(messages, system=None, temperature=1.0, stop_sequences=[], tools=None)` builds the
  request params and calls `client.messages.create(...)`. `system` and `tools` are only
  added when provided.
- `add_user_message(messages, text)` / `add_assistant_message(messages, text)` append
  correctly-shaped message dicts so conversation history stays consistent.

The model is set here (`claude-sonnet-4-6`).

## 2. The tool registry — `tools/registry.py`

A tool is two things: a **schema** (what Claude sees) and a **function** (what runs).

```python
# schemas advertised to Claude
TOOLS = [market_tools.get_current_datetime_schema,
         market_tools.get_stock_prices_schema]

# name -> implementation
TOOL_FUNCTION = {
    "get_current_datetime": market_tools.get_current_datetime,
    "get_stock_prices": market_tools.get_stock_prices,
}

def run_tools(tool_name, tool_input):
    return TOOL_FUNCTION[tool_name](**tool_input)
```

`run_tools` is the single dispatch point: it looks up the function by name and calls it with
the input Claude provided. This keeps the loop independent of *which* tools exist.

## 3. The agent loop — `chat_agent.py`

`run_conversations(messages)` is the heart of the agent:

1. Call `chat(messages, tools=TOOLS)`.
2. Append Claude's response to history (`add_assistant_message`).
3. **If `stop_reason != "tool_use"`** → Claude is done; return the joined text. ✅
4. Otherwise, for **every** `tool_use` block in the response:
   - call `run_tools(block.name, block.input)`
   - on success, append a `tool_result` with the JSON-serialized output
   - on exception, append a `tool_result` with `is_error: True` so Claude learns it failed
5. Append all results as **one** `user` message and loop back to step 1.

Two design points make multi-tool calling work:

- **Looping until done** (step 3) enables **serial** calls — Claude can call a tool, see the
  result on the next iteration, and decide what to call next.
- **Iterating over all blocks** (step 4) enables **parallel** calls — when Claude returns
  several `tool_use` blocks in one response, they're all executed before looping.

See [Multi-Tool Calling](multi-tool-calling.md) for how these two behaviors play out.
