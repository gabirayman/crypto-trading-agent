from typing import List, Dict, Any
from exchanges.client import fetch_account_balance, fetch_price, execute_order
from logic.rebalance_by_percentage import calculate_rebalance_plan

def get_portfolio_data() -> Dict[str, Any]:
    """
    Fetches balances and calculates total USD value.
    Returns: {'balances': {'BTC': 0.5}, 'total_usdt': 50000.0, 'prices': {...}}
    """
    balances = fetch_account_balance()
    if isinstance(balances, str) and "Error" in balances:
        raise ConnectionError(balances)
    
    # Get prices for everything we own
    prices = {}
    total_value = 0.0
    
    for asset, amount in balances.items():
        if asset == "USDT":
            total_value += amount
            prices["USDT/USDT"] = 1.0
        else:
            price = fetch_price(f"{asset.upper()}/USDT")
            if isinstance(price, (int, float)):
                prices[f"{asset}/USDT"] = price
                total_value += amount * price
                
    return {
        "balances": balances,
        "prices": prices,
        "total_value_usdt": round(total_value, 2)
    }



def generate_rebalance_plan(target_allocations: Dict[str, float]) -> List[Dict[str, Any]]:
    """
    Full Workflow: Fetches Balances -> Fetches Needed Prices -> Calculates Trades.
    Returns a list of trade instructions.
    """
    # Validation: Ensure targets sum to ~1.0
    total_pct = sum(target_allocations.values())
    if not (0.99 <= total_pct <= 1.01):
        raise ValueError(f"Targets must sum to 100% (got {total_pct*100}%)")
    
    # Step A: Fetch Balances
    balances = fetch_account_balance()
    if isinstance(balances, str) and "Error" in balances:
        raise ConnectionError(f"Failed to fetch balances: {balances}")

    # Step B: Identify ALL assets we need prices for (Current Holdings + New Targets)
    needed_assets = set(balances.keys()) | set(target_allocations.keys())
    current_prices = {}
    
    # Step C: Fetch Prices efficiently
    for asset in needed_assets:
        if asset == "USDT":
            continue # USDT is always $1
        
        # Fetch price and store it
        price = fetch_price(f"{asset.upper()}/USDT")
        
        # If price fetch failed, we skip it (can't trade what we can't price)
        if isinstance(price, (int, float)):
            current_prices[f"{asset}/USDT"] = price

    # Step D: Run the Math
    trades = calculate_rebalance_plan(balances, current_prices, target_allocations)
    
    return trades

def execute_rebalance_trades(trades: List[Dict[str, Any]]) -> List[str]:
    """
    Takes a list of proposed trades and executes them.
    Returns a log of what happened.
    """
    results = []
    
    for trade in trades:
        asset = trade['asset']
        action = trade['action'].lower() # 'buy' or 'sell'
        amount = trade['amount']
        symbol = f"{asset.upper()}/USDT"
        
        # Execute
        results.append(f"Executing: {action.upper()} {amount} {asset}...")
        
        response = execute_order(symbol, action, amount)
        
        if response['status'] == 'success':
            results.append(f"✅ Success! Order ID: {response['id']} | Price: {response['price']}")
        elif response['status'] == 'skipped':
            results.append(f"⚠️ Skipped: {response['reason']}")
        else:
            results.append(f"❌ Failed: {response.get('error', 'Unknown Error')}")
            
    return results

def execute_single_trade(asset: str, action: str, amount: float) -> Dict[str, Any]:
    """
    Executes a single trade order.
    Args:
        asset: 'BTC'
        action: 'buy' or 'sell'
        amount: quantity of the asset to trade
    Returns:
        Response dict from execute_order
    """
    symbol = f"{asset.upper()}/USDT"
    return execute_order(symbol, action.lower(), amount)





    



