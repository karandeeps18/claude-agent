# Adding a Tool

A tool is **two things**: a Python function and a JSON schema describing it to Claude.
Adding one takes three steps.

## Step 1 — Write the function and schema

In `claude_agent/tools/market_tools.py` (or a new module under `tools/`), define the
function and a matching `ToolParam` schema. Here's a small example tool that returns the
day-over-day percentage change between two closing prices:

```python
def pct_change(old: float, new: float):
    if old == 0:
        raise ValueError("old price cannot be zero")
    return {"pct_change": round((new - old) / old * 100, 2)}

pct_change_schema = ToolParam({
    "name": "pct_change",
    "description": (
        "Computes the percentage change from an old value to a new value. "
        "Returns {'pct_change': <number>} where a positive value is an increase."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "old": {"type": "number", "description": "The starting/old value."},
            "new": {"type": "number", "description": "The ending/new value."},
        },
        "required": ["old", "new"],
    },
})
```

!!! tip "Write the description for Claude, not for humans"
    The `description` is how Claude decides *when* and *how* to call the tool. Be explicit
    about the output shape, edge cases, and when **not** to use it. The existing
    `get_stock_prices_schema` is a good model — it spells out the row shape, that weekends
    are absent, and that an empty result is valid, not a failure.

## Step 2 — Register it

In `claude_agent/tools/registry.py`, add the schema to `TOOLS` and the name→function
mapping to `TOOL_FUNCTION`:

```python
TOOLS = [
    market_tools.get_current_datetime_schema,
    market_tools.get_stock_prices_schema,
    market_tools.pct_change_schema,        # ← add schema
]

TOOL_FUNCTION = {
    "get_current_datetime": market_tools.get_current_datetime,
    "get_stock_prices": market_tools.get_stock_prices,
    "pct_change": market_tools.pct_change,  # ← add function
}
```

!!! warning "Name must match"
    The `"name"` in the schema, the key in `TOOL_FUNCTION`, and what Claude calls must all be
    identical. `run_tools` looks the function up by that exact name.

## Step 3 — Run it

That's all — no changes to the agent loop. Start the agent and ask something that needs the
new tool:

```bash
python -m claude_agent.chat_agent
```

```text
You: AAPL went from 201.45 to 209.00 — what's the percent change?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling pct_change({'old': 201.45, 'new': 209.0})

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: That's a +3.75% change.
```

## Conventions worth following

- **Return JSON-serializable data** (dicts, lists, numbers, strings). The loop does
  `json.dumps(result)` on the output.
- **Raise on real errors.** The loop catches exceptions and reports them to Claude with
  `is_error: True`, so raising a clear `ValueError` is the right move for bad input.
- **Return a structured "empty" result** for valid-but-no-data cases (like
  `get_stock_prices` returning `rows: []` with a `note`) rather than raising.
