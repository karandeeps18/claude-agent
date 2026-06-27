# Examples

Annotated input/output transcripts. The trace lines (`--- API Call ... ---` and
`tool calling ...`) are exactly what `run_conversations` prints, so you can match these
against your own runs.

!!! info "Illustrative outputs"
    Prices and timestamps below are illustrative, chosen to show the mechanics. Your live
    runs will return real Yahoo Finance data for the dates you ask about.

---

## Example 1 — Single tool call

The simplest case: one tool, one round-trip of work.

```text
You: What's the date today?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_current_datetime({'date_format': '%Y-%m-%d'})

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: Today is 2026-06-27.
```

**Behind the scenes:** Claude returns one `tool_use` block → the loop runs
`get_current_datetime` → appends the `tool_result` → next API call has `stop_reason=end_turn`,
so the loop returns the text.

---

## Example 2 — Serial (dependent) multi-tool

The second call needs the first call's output, so they happen across separate round-trips.

```text
You: What was Apple's closing price yesterday?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_current_datetime({'date_format': '%Y-%m-%d'})
    → "2026-06-27"

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_stock_prices({'ticker': 'AAPL', 'start_date': '2026-06-26'})
    → {"ticker": "AAPL", "rows": [{"date": "2026-06-26", "close": 201.45}]}

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: Apple (AAPL) closed at $201.45 on 2026-06-26.
```

**Why serial:** Claude can't request "yesterday's price" until it knows today's date. The
`while True` loop gives it a second turn to act on the date it just received.

---

## Example 3 — Parallel (independent) multi-tool

Two independent lookups requested in a single response.

```text
You: Compare the closing prices of AAPL and MSFT on 2025-01-15.

--- API Call: stop_response=tool_use, 2 tool_use block(s) ---
tool calling get_stock_prices({'ticker': 'AAPL', 'start_date': '2025-01-15'})
    → {"ticker": "AAPL", "rows": [{"date": "2025-01-15", "close": 234.40}]}
tool calling get_stock_prices({'ticker': 'MSFT', 'start_date': '2025-01-15'})
    → {"ticker": "MSFT", "rows": [{"date": "2025-01-15", "close": 426.31}]}

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: On 2025-01-15, AAPL closed at $234.40 and MSFT at $426.31 — MSFT was higher.
```

**Why parallel:** the two prices don't depend on each other, so Claude emits **two**
`tool_use` blocks at once (note `2 tool_use block(s)`). The loop runs both and returns both
results in one `user` message.

---

## Example 4 — Error handling

When a tool raises, the agent reports the failure back to Claude with `is_error: True`
instead of crashing — and Claude can recover gracefully.

```text
You: What's the close for ticker ZZZZ on 2025-01-15?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_stock_prices({'ticker': 'ZZZZ', 'start_date': '2025-01-15'})
    → {"ticker": "ZZZZ", "rows": [],
       "note": "No trading days in the window or Invalid ticker."}

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: I couldn't find any price data for "ZZZZ" on 2025-01-15 — it may not be a
valid ticker. Want me to try a different symbol?
```

!!! note "Empty result vs. raised error"
    `get_stock_prices` treats an unknown ticker as a **valid empty result** (`rows: []` with
    a `note`), not an exception. The `is_error: True` path in the loop fires only when a tool
    actually **raises** — for example, calling `get_current_datetime` with an empty format
    string raises `ValueError`, which the loop catches and reports back to Claude.
