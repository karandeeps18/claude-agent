# Claude Multi-Tool Agent

> A minimal Claude agent that demonstrates **serial** and **parallel** tool calling, built on the Anthropic Python SDK.

[![Python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/)
[![Docs](https://img.shields.io/badge/docs-github%20pages-success.svg)](https://karandeeps18.github.io/claude-agent/)

📖 **Full documentation:** https://karandeeps18.github.io/claude-agent/

---

## Overview

This project is a compact, readable reference implementation of a **tool-calling agent**.
Claude decides which tools to call, the agent executes them, feeds the results back, and
loops until Claude produces a final answer. It is intentionally small so the **multi-tool
calling mechanics** are easy to follow:

- **Serial** tool calls — Claude calls a tool, uses its result to decide the *next* call.
- **Parallel** tool calls — Claude requests several independent tools in a single turn.

It ships with two example tools: `get_current_datetime` and `get_stock_prices` (Yahoo Finance).

## Demo

```text
You: What was Apple's closing price yesterday?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_current_datetime({'date_format': '%Y-%m-%d'})

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_stock_prices({'ticker': 'AAPL', 'start_date': '2026-06-26'})

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: Apple (AAPL) closed at $201.45 on 2026-06-26.
```

## Features

- 🔁 **Serial (multi-step) tool calling** via a re-entrant agent loop
- ⚡ **Parallel (same-turn) tool calling** — multiple `tool_use` blocks per response
- 🧩 **Pluggable tool registry** — a tool = JSON schema + Python function
- 🛡️ **Per-tool error handling** surfaced back to Claude with `is_error`
- 📈 **Built-in tools:** `get_current_datetime`, `get_stock_prices`

## Architecture

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

The loop lives in [`claude_agent/chat_agent.py`](claude_agent/chat_agent.py). Each iteration
calls the API; if Claude wants tools (`stop_reason == "tool_use"`), the agent runs **all**
requested tools, appends their results as one `user` message, and loops. When Claude stops
asking for tools, the loop returns the final text.

Tools are wired through a small **registry** ([`claude_agent/tools/registry.py`](claude_agent/tools/registry.py)):
`TOOLS` holds the schemas advertised to Claude, and `TOOL_FUNCTION` maps each tool name to
the Python function that implements it.

## How Multi-Tool Calling Works

**Serial (dependent):** "What was AAPL's close yesterday?" → Claude calls
`get_current_datetime` to learn today's date, *then* uses that to call `get_stock_prices`.
Two API round-trips, because the second call depends on the first.

**Parallel (independent):** "Compare AAPL and MSFT closes for Jan 15." → Claude emits *two*
`get_stock_prices` `tool_use` blocks in one response; the agent runs both and returns both
results together. One round-trip.

See the [Multi-Tool Calling guide](https://karandeeps18.github.io/claude-agent/multi-tool-calling/)
and [Examples](https://karandeeps18.github.io/claude-agent/examples/) for full traces.

## Project Structure

```
claude_agent/
  chat_agent.py           # the agent loop (run_conversations) + CLI entry point
  anthropic_client.py     # thin Anthropic SDK wrapper: chat(), message helpers
  tools/
    registry.py           # TOOLS (schemas) + TOOL_FUNCTION map + run_tools()
    market_tools.py       # get_current_datetime, get_stock_prices + their schemas
docs/                     # MkDocs documentation source
mkdocs.yml                # docs site config
requirements.txt          # runtime + docs dependencies
```

## Getting Started

### Prerequisites
- Python 3.13+
- An Anthropic API key
- Internet access (yfinance fetches live market data)

### Installation
```bash
git clone https://github.com/karandeeps18/claude-agent.git
cd claude-agent
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project root:
```bash
ANTHROPIC_API_KEY=sk-ant-...
```

### Running
```bash
python -m claude_agent.chat_agent
```
Then chat in the terminal. Type `exit` or `quit` to stop.

## Adding a New Tool

1. **Write the function and its schema** in `claude_agent/tools/market_tools.py`
   (or a new module): a Python function plus a matching `ToolParam` schema.
2. **Register it** in `claude_agent/tools/registry.py`: add the schema to `TOOLS` and the
   `name -> function` entry to `TOOL_FUNCTION`.
3. That's it — Claude can now call it. See the
   [Adding a Tool guide](https://karandeeps18.github.io/claude-agent/adding-a-tool/).

## Tools Reference

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `get_current_datetime` | Current local date/time, `strftime`-formatted | `date_format` (optional) | formatted string |
| `get_stock_prices` | Daily closing prices (Yahoo Finance) | `ticker`, `start_date`, `end_date?` | `{ticker, rows:[{date, close}]}` |

## Limitations

- Returns **closing prices only** (no open/high/low/volume).
- Only trading days appear in results; weekends/holidays are omitted by design.
- No response streaming; the loop blocks per API call.
- Conversation history is in-memory only (lost when the process exits).
