###################################################
# first version
###################################################

# from fastmcp import FastMCP
# from exchanges.client import fetch_price

# # Initialize the MCP Server
# mcp = FastMCP("Crypto Rebalancer")

# @mcp.tool()
# def get_crypto_price(asset: str) -> str:
#     """
#     Get the current price of a crypto asset in USDT.
#     Args:
#         asset: The ticker symbol (e.g., BTC, ETH, SOL)
#     """
#     # Force uppercase for consistency
#     symbol = f"{asset.upper()}/USDT"
    
#     price = fetch_price(symbol)
    
#     if isinstance(price, str) and "Error" in price:
#         return f"Could not fetch price for {asset}. Reason: {price}"
        
#     return f"The current price of {asset} is ${price}"

# if __name__ == "__main__":
#     mcp.run()

###################################################
# second version
###################################################

# from fastmcp import FastMCP
# from exchanges.client import fetch_price, fetch_account_balance 

# mcp = FastMCP("Crypto Rebalancer")

# @mcp.tool()
# def get_crypto_price(asset: str) -> str:
#     """
#     Get the current price of a crypto asset in USDT.
#     Args:
#         asset: The ticker symbol (e.g., BTC, ETH, SOL)
#     """
#     symbol = f"{asset.upper()}/USDT"
#     price = fetch_price(symbol)
    
#     if isinstance(price, str) and "Error" in price:
#         return f"Could not fetch price for {asset}. Reason: {price}"
        
#     return f"The current price of {asset} is ${price}"

# @mcp.tool()
# def get_my_portfolio() -> str:
#     """
#     Get the current non-zero balances in the user's portfolio.
#     """
#     data = fetch_account_balance()
    
#     if isinstance(data, str) and "Error" in data:
#         return f"Could not fetch balance. Check your API Keys. Details: {data}"
    
#     # Filter: Only show assets where you have money
#     # data looks like: {'BTC': 0.5, 'ETH': 0.0, 'XRP': 0.0 ...}
#     my_assets = []
#     for asset, amount in data.items():
#         if amount > 0:
#             my_assets.append(f"- {asset}: {amount}")
            
#     if not my_assets:
#         return "Your portfolio is empty (0 balance)."
        
#     return "Current Portfolio:\n" + "\n".join(my_assets)

# if __name__ == "__main__":
#     mcp.run()

###################################################
# third version with rebalance tool
###################################################

import json
from fastmcp import FastMCP
from exchanges.client import fetch_price, fetch_account_balance
# We import your renamed logic file here:
from logic.rebalance_by_percentage import calculate_rebalance_plan

mcp = FastMCP("Crypto Rebalancer")

@mcp.tool()
def get_crypto_price(asset: str) -> str:
    """
    Get the current price of a crypto asset in USDT.
    """
    symbol = f"{asset.upper()}/USDT"
    price = fetch_price(symbol)
    if isinstance(price, str) and "Error" in price:
        return f"Error: {price}"
    return f"${price}"

@mcp.tool()
def get_my_portfolio() -> str:
    """
    Get current non-zero balances.
    """
    data = fetch_account_balance()
    if isinstance(data, str) and "Error" in data:
        return data
    
    # Filter for non-zero assets
    lines = []
    for asset, amount in data.items():
        if amount > 0:
            lines.append(f"{asset}: {amount}")
            
    if not lines:
        return "Portfolio is empty."
    return "\n".join(lines)

@mcp.tool()
def plan_portfolio_rebalance(target_percentages: str) -> str:
    """
    Calculates a rebalance plan based on target percentages.
    
    Args:
        target_percentages: A JSON string of targets summing to 1.0 (e.g. '{"BTC": 0.5, "ETH": 0.5}')
    """
    try:
        # 1. Parse the User's Input
        targets = json.loads(target_percentages)
        
        # 2. Get Real Data (Balances)
        balances = fetch_account_balance()
        if isinstance(balances, str) and "Error" in balances:
            return f"Error fetching balances: {balances}"

        # 3. Get Real Data (Prices)
        # We need prices for BOTH what we have AND what we want
        needed_prices = set(balances.keys()) | set(targets.keys())
        current_prices = {}
        
        for asset in needed_prices:
            if asset == "USDT":
                continue # USDT is always $1
            
            # Fetch price and store it
            price = fetch_price(f"{asset.upper()}/USDT")
            if not isinstance(price, (int, float)):
                continue # Skip assets where price fetch failed
            current_prices[f"{asset}/USDT"] = price

        # 4. The "Brain" (Your Logic File)
        trades = calculate_rebalance_plan(balances, current_prices, targets)
        
        # 5. Format the Output for the Chat
        if not trades:
            return "No trades needed! Your portfolio is already balanced."
            
        summary = "Proposed Rebalance Plan:\n"
        for trade in trades:
            summary += f"- {trade['action']} ${trade['value_usdt']} worth of {trade['asset']} ({trade['amount']} coins)\n"
            
        return summary

    except Exception as e:
        return f"Calculation failed: {str(e)}"

if __name__ == "__main__":
    mcp.run()