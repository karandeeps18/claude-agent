# Tools Reference

The built-in tools live in [`claude_agent/tools/market_tools.py`](https://github.com/karandeeps18/claude-agent/blob/main/claude_agent/tools/market_tools.py).

| Tool | Description | Inputs | Output |
|------|-------------|--------|--------|
| `get_current_datetime` | Current local date/time, formatted with a `strftime` string | `date_format` *(optional)* | formatted string |
| `get_stock_prices` | Daily **closing** prices from Yahoo Finance | `ticker`, `start_date`, `end_date` *(optional)* | `{ticker, rows: [{date, close}]}` |

---

## `get_current_datetime`

Returns the current local date/time as a single formatted string. Does not handle time
zones or past/future dates.

**Inputs**

| Name | Type | Required | Default | Notes |
|------|------|----------|---------|-------|
| `date_format` | string | no | `"%Y-%m-%d %H:%M:%S"` | Python `strftime` directives. Must be non-empty. |

**Output:** a string, e.g. `"2026-06-27 14:32:08"`.

**Errors:** raises `ValueError` if `date_format` is an empty string.

```python
get_current_datetime()                 # "2026-06-27 14:32:08"
get_current_datetime("%Y-%m-%d")       # "2026-06-27"
```

---

## `get_stock_prices`

Fetches historical daily **closing** prices (no open/high/low/volume).

**Inputs**

| Name | Type | Required | Notes |
|------|------|----------|-------|
| `ticker` | string | yes | Yahoo Finance symbol, e.g. `AAPL`, `MSFT`, `TSLA`. |
| `start_date` | string | yes | `YYYY-MM-DD`. First day of the window. |
| `end_date` | string | no | `YYYY-MM-DD`, **inclusive**. If omitted, only `start_date` is priced. |

**Output:** an object with the ticker and a `rows` list:

```json
{
  "ticker": "AAPL",
  "rows": [
    {"date": "2025-01-15", "close": 234.40},
    {"date": "2025-01-16", "close": 237.87}
  ]
}
```

**Behavior notes**

- `end_date` is **inclusive**: internally the tool adds one day to build the exclusive
  range yfinance expects.
- Only **trading days** appear in `rows` — weekends and market holidays are simply absent.
  That's normal, not an error.
- If there's no data (no trading days in the window, or an unknown ticker), `rows` is an
  empty list with a `note`. This is a **valid result**, not a failure to retry:

```json
{"ticker": "ZZZZ", "rows": [], "note": "No trading days in the window or Invalid ticker."}
```

```python
get_stock_prices("AAPL", "2025-01-15")                    # single day
get_stock_prices("MSFT", "2025-01-01", "2025-01-31")      # inclusive range
```
