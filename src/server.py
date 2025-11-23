import json
from fastmcp import FastMCP
from exchanges.client import fetch_price, fetch_account_balance, execute_order
from logic.portfolio_manager import generate_rebalance_plan, execute_rebalance_trades, execute_single_trade, get_portfolio_data
from config_manager import set_min_threshold, update_sub_wallet

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
    
    lines = []
    for asset, amount in data.items():
        lines.append(f"{asset}: {amount}")
            
    if not lines:
        return "Portfolio is empty."
    return "\n".join(lines)

@mcp.tool()
def plan_portfolio_rebalance(target_percentages: str) -> str:
    """
    Calculates a rebalance plan. 
    Input must be a JSON string like: '{"BTC": 0.5, "ETH": 0.5}'
    """
    try:
        # 1. Parse the Input (Chat Layer)
        targets = json.loads(target_percentages)
        
        # 2. Call the Business Logic (Service Layer)
        trades = generate_rebalance_plan(targets)
        
        # 3. Format the Output (Presentation Layer)
        if not trades:
            return "No trades needed. Portfolio is balanced."
            
        return json.dumps(trades, indent=2)

    except json.JSONDecodeError:
        return "Error: Invalid JSON format. Please provide targets like '{\"BTC\": 0.5}'"
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def create_sub_wallet(coins_list: str) -> str:
    """
    Creates a sub-wallet configuration from a comma-separated list of coins.
    Example input: '["BTC", "ETH", "SOL"]'
    """
    try:
        coins = json.loads(coins_list)
        if not isinstance(coins, list) or not all(isinstance(c, str) for c in coins):
            return "Error: Please provide a JSON array of coin symbols."
        
        update_sub_wallet(coins)
        return f"Sub-wallet created with assets: {', '.join(coins)}"
    except json.JSONDecodeError:
        return "Error: Invalid JSON format. Please provide a list like '[\"BTC\", \"ETH\"]'."
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def set_min_balance_threshold(threshold_value: float) -> str:
    """
    Sets the minimum balance threshold for filtering assets.
    Example input: 10.0
    """
    try:
        if threshold_value < 0:
            return "Error: Threshold must be non-negative."
        
        set_min_threshold(threshold_value)
        return f"Minimum balance threshold set to {threshold_value}."
    except Exception as e:
        return f"System Error: {str(e)}"

@mcp.tool()
def execute_trading_plan(trades_json: str) -> str:
    """
    Executes the list of trades. 
    WARNING: This will move real funds if not in Sandbox Mode.
    
    Args:
        trades_json: The JSON string returned by 'plan_portfolio_rebalance'.
                     Example: '[{"action": "SELL", "asset": "BTC", "amount": 0.1, ...}]'
    """
    try:
        # 1. Parse the plan
        trades = json.loads(trades_json)
        
        if not isinstance(trades, list):
            return "Error: Input must be a list of trades."
            
        if not trades:
            return "No trades to execute."

        # 2. Execute
        logs = execute_rebalance_trades(trades)
        
        return "\n".join(logs)

    except json.JSONDecodeError:
        return "Error: Invalid JSON format."
    except Exception as e:
        return f"Execution Error: {str(e)}"

@mcp.tool()
def trade_single(trade_json: str) -> str:
    """
    Execute a single trade.
    Input JSON example: '{"asset": "BTC", "action": "sell", "amount": 0.1}'
    """
    try:
        data = json.loads(trade_json)
        asset = data.get("asset")
        action = data.get("action")
        amount = data.get("amount")

        # if not asset or not isinstance(asset, str):
        #     return "Error: 'asset' must be a non-empty string."
        # if not action or not isinstance(action, str) or action.lower() not in ("buy", "sell"):
        #     return "Error: 'action' must be 'buy' or 'sell'."
        # try:
        #     amount = float(amount)
        # except Exception:
        #     return "Error: 'amount' must be a number."
        # if amount <= 0:
        #     return "Error: 'amount' must be greater than zero."

        result = execute_single_trade(asset, action, amount)
        return json.dumps(result, indent=2)

    except json.JSONDecodeError:
        return "Error: Invalid JSON format. Provide like '{\"asset\":\"BTC\",\"action\":\"sell\",\"amount\":0.1}'."
    except Exception as e:
        return f"Execution Error: {str(e)}"

@mcp.tool()
def get_total_portfolio_value() -> str:
    """
    Calculates the total value of the portfolio in USDT.
    """
    try:
        # Reuse our existing logic function
        data = get_portfolio_data()
        
        total_value = data.get('total_value_usdt', 0.0)
        
        # Format nicely with commas (e.g., $10,234.56)
        return f"Total Portfolio Value: ${total_value:,.2f} USDT"
        
    except Exception as e:
        return f"Error calculating value: {str(e)}"

if __name__ == "__main__":
    mcp.run()