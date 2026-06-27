# Multi-Tool Calling

"Multi-tool calling" covers two distinct patterns. The agent loop in
[`chat_agent.py`](architecture.md#3-the-agent-loop-chat_agentpy) supports **both** with the
same code.

| | **Serial** | **Parallel** |
|---|---|---|
| Relationship | each call **depends** on the previous result | calls are **independent** |
| API round-trips | one per step (N calls → N+1 round-trips) | a single round-trip for all calls |
| Driven by | the `while True` loop re-calling the API | iterating over all `tool_use` blocks in one response |
| Example | "yesterday's AAPL close" (need date → then price) | "compare AAPL and MSFT on Jan 15" |

## Serial (dependent) calls

Claude calls one tool, **uses its result** to choose the next call. This is sequential by
necessity — the second input isn't known until the first returns.

```text
User: "What was Apple's closing price yesterday?"

Round-trip 1 ─ Claude doesn't know today's date.
  stop_reason = tool_use
  tool_use: get_current_datetime({'date_format': '%Y-%m-%d'})
  → "2026-06-27"

Round-trip 2 ─ Claude now computes "yesterday" and asks for the price.
  stop_reason = tool_use
  tool_use: get_stock_prices({'ticker': 'AAPL', 'start_date': '2026-06-26'})
  → {"ticker": "AAPL", "rows": [{"date": "2026-06-26", "close": 201.45}]}

Round-trip 3 ─ Claude has everything it needs.
  stop_reason = end_turn
  → "Apple (AAPL) closed at $201.45 on 2026-06-26."
```

**What makes it work:** the `while True` loop. After each tool result is appended, the loop
calls the API again, giving Claude a fresh turn to act on what it just learned.

## Parallel (independent) calls

When tasks don't depend on each other, Claude can request them **all at once** — multiple
`tool_use` blocks in a single response. The agent runs them all and returns the results
together.

```text
User: "Compare the closing prices of AAPL and MSFT on 2025-01-15."

Round-trip 1 ─ both prices are independent, so Claude asks for both at once.
  stop_reason = tool_use, 2 tool_use block(s)
  tool_use: get_stock_prices({'ticker': 'AAPL', 'start_date': '2025-01-15'})
  tool_use: get_stock_prices({'ticker': 'MSFT', 'start_date': '2025-01-15'})
  → AAPL: {"rows": [{"date": "2025-01-15", "close": 234.40}]}
  → MSFT: {"rows": [{"date": "2025-01-15", "close": 426.31}]}

Round-trip 2 ─ Claude compares and answers.
  stop_reason = end_turn
  → "On 2025-01-15, AAPL closed at $234.40 and MSFT at $426.31 — MSFT was higher."
```

**What makes it work:** the loop iterates over **every** `tool_use` block in the response
and collects all `tool_result`s into one `user` message before looping. The two prices are
fetched in the same turn rather than over two round-trips.

!!! note "Claude decides the pattern, not your code"
    You don't switch modes manually. Claude chooses serial vs parallel based on whether the
    tasks depend on each other. The agent's job is simply to **handle both**: loop until
    done (serial) and run all blocks per turn (parallel).

See full annotated runs on the [Examples](examples.md) page.
