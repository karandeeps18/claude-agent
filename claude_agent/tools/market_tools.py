from anthropic.types import ToolParam
from datetime import datetime, timedelta
import yfinance as yf 
import pandas as pd

# tool function - get current datetime 
def get_current_datetime(date_format="%Y-%m-%d %H:%M:%S"):
    # validate input 
    if not date_format:
        raise ValueError("Date_format cannot be empty")
    return datetime.now().strftime(date_format)

# current datetime schema 
get_current_datetime_schema = ToolParam({
  "name": "get_current_datetime",
  "description": "Retrieves the current local date and time, formatted according to a Python strftime format string. Use this tool whenever you need to know the present date or time, for example to timestamp an event, calculate durations from now, or answer questions about the current date/time. The tool returns a single formatted string based on the system's current local time at the moment of the call. It does not accept or convert between time zones, and it does not return past or future dates. The format string must be non-empty; an empty format string is rejected as invalid.",
  "input_schema": {
    "type": "object",
    "properties": {
      "date_format": {
        "type": "string",
        "description": "A Python strftime-compatible format string specifying how the returned date/time should be formatted (e.g. '%Y-%m-%d' for '2026-06-04', or '%Y-%m-%d %H:%M:%S' for '2026-06-04 14:30:00'). Common directives: %Y (4-digit year), %m (month), %d (day), %H (24-hour), %M (minute), %S (second). Must not be empty. Defaults to '%Y-%m-%d %H:%M:%S' if omitted."
      }
    },
    "required": []
  },
  "input_examples": [
    { "date_format": "%Y-%m-%d %H:%M:%S" },
    { "date_format": "%Y-%m-%d" },
    {}
  ]
})

# Fetch the stock price using yfinance
def get_stock_prices(ticker: str, start_date: str, end_date: str = None):
    stock = yf.Ticker(ticker)
    
    end_base = end_date or start_date
    
    # end-date is exclusive +1 
    end = (datetime.strptime(end_base, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
    price_data = stock.history(start=start_date, end=end)
    
    # return a structured json for the given df 
    if price_data.empty:
        return {"ticker": ticker, "rows": [], 
                "note": "No trading days in the window or Invalid ticker."}
    
    price_data.index = price_data.index.date
    rows = []
    for d, p in price_data["Close"].items():
        rows.append({"date": str(d), "close": float(round(p, 2))})
    
    return {"ticker": ticker, "rows": rows}
  
get_stock_prices_schema = ToolParam({
    "name": "get_stock_prices",
    "description": (
        "Fetches historical daily CLOSING stock prices for a publicly traded company "
        "(Yahoo Finance). Always returns the same structure: an object with the ticker and "
        "a 'rows' list, where each row is {\"date\": \"YYYY-MM-DD\", \"close\": <number>}. "
        "Single day: provide only start_date (end_date defaults to that same day) and 'rows' "
        "has one entry. Date range: provide start_date and end_date and 'rows' covers every "
        "trading day from start_date through end_date INCLUSIVE. "
        "Only trading days appear in 'rows' — weekends and market holidays are simply absent, "
        "which is normal, not an error; the tool already knows the market calendar, so never "
        "work out trading days yourself or call this once per date in a loop. To get the last "
        "N trading days, request a range covering roughly 2N calendar days and take the last N "
        "rows. Returns closing prices only (no open/high/low/volume). If there is no data, "
        "'rows' is an empty list with a 'note' — a VALID result meaning the window had no "
        "trading days or the ticker is unknown, NOT a failure to retry."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "ticker": {
                "type": "string",
                "description": "Stock ticker symbol recognized by Yahoo Finance, e.g. 'AAPL', 'MSFT', 'TSLA'."
            },
            "start_date": {
                "type": "string",
                "description": "First day of the window, 'YYYY-MM-DD'. In single-day mode this is the day priced."
            },
            "end_date": {
                "type": "string",
                "description": "Optional last day of the window, 'YYYY-MM-DD', INCLUSIVE (the returned rows include end_date). If omitted, only start_date is priced."
            }
        },
        "required": ["ticker", "start_date"]
    },
    "input_examples": [
        { "ticker": "AAPL", "start_date": "2025-01-15" },
        { "ticker": "MSFT", "start_date": "2025-01-01", "end_date": "2025-01-31" },
        { "ticker": "NVDA", "start_date": "2024-06-03", "end_date": "2024-06-07" }
    ]
})


if __name__ == "__main__":
   price =  get_stock_prices("SPCX", "2026-06-22")
   print(price)