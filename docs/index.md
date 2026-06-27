# Claude Multi-Tool Agent

> A minimal Claude agent that demonstrates **serial** and **parallel** tool calling, built on the Anthropic Python SDK.

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

## Where to go next

<div class="grid cards" markdown>

- :material-rocket-launch: **[Getting Started](getting-started.md)** — install, configure, run.
- :material-sitemap: **[Architecture](architecture.md)** — the agent loop and registry pattern.
- :material-call-split: **[Multi-Tool Calling](multi-tool-calling.md)** — serial vs parallel, explained.
- :material-console: **[Examples](examples.md)** — annotated input/output transcripts.
- :material-puzzle: **[Adding a Tool](adding-a-tool.md)** — extend the agent in 3 steps.
- :material-book-open-variant: **[Tools Reference](tools-reference.md)** — schemas and I/O shapes.

</div>

## Features

- 🔁 **Serial (multi-step) tool calling** via a re-entrant agent loop
- ⚡ **Parallel (same-turn) tool calling** — multiple `tool_use` blocks per response
- 🧩 **Pluggable tool registry** — a tool = JSON schema + Python function
- 🛡️ **Per-tool error handling** surfaced back to Claude with `is_error`
- 📈 **Built-in tools:** `get_current_datetime`, `get_stock_prices`
