from claude_agent.tools import market_tools

#  list of available tool schema for the agent
TOOLS = [market_tools.get_current_datetime_schema, market_tools.get_stock_prices_schema]

# mapping of tool names to the actual tool functions 
TOOL_FUNCTION = {
    "get_current_datetime" : market_tools.get_current_datetime, 
    "get_stock_prices": market_tools.get_stock_prices,
}

#  
def run_tools(tool_name, tool_input):
    return TOOL_FUNCTION[tool_name](**tool_input)