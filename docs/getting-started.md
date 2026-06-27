# Getting Started

## Prerequisites

- **Python 3.13+**
- An **Anthropic API key** ([console.anthropic.com](https://console.anthropic.com/))
- **Internet access** — `get_stock_prices` fetches live data from Yahoo Finance

## Installation

```bash
git clone https://github.com/karandeeps18/claude-agent.git
cd claude-agent

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the project root. The Anthropic SDK reads `ANTHROPIC_API_KEY`
automatically (loaded via `python-dotenv` in `anthropic_client.py`):

```bash
ANTHROPIC_API_KEY=sk-ant-...
```

!!! warning "Keep your key secret"
    `.env` is already listed in `.gitignore`. Never commit your API key.

## Running

Start the interactive CLI:

```bash
python -m claude_agent.chat_agent
```

You'll get a `You:` prompt. Type a question and watch the agent's tool-calling trace,
followed by the assistant's final answer. Type `exit` or `quit` to stop.

```text
You: What time is it right now?

--- API Call: stop_response=tool_use, 1 tool_use block(s) ---
tool calling get_current_datetime({})

--- API Call: stop_response=end_turn, 0 tool_use block(s) ---
Assistant: It's currently 2026-06-27 14:32:08 (local time).
```

!!! tip "Running the modules directly"
    Both `chat_agent.py` and `anthropic_client.py` have `__main__` blocks for quick
    manual checks. Run them as modules from the project root so the
    `claude_agent.*` imports resolve:
    `python -m claude_agent.anthropic_client`.
