from typing import Dict, List, Any

def calculate_rebalance_plan(
    current_balances: Dict[str, float], 
    current_prices: Dict[str, float], 
    target_allocations: Dict[str, float]
) -> List[Dict[str, Any]]:
    """
    Calculates the trades needed to match the target allocation.
    
    Args:
        current_balances: {'BTC': 0.5, 'USDT': 1000.0}
        current_prices: {'BTC/USDT': 50000.0, 'ETH/USDT': 3000.0}
        target_allocations: {'BTC': 0.5, 'ETH': 0.5} (Must sum to 1.0)
        
    Returns:
        List of trades: [{'action': 'SELL', 'asset': 'BTC', 'amount': 0.1}, ...]
    """
    
    # 1. Calculate Total Portfolio Value in USDT
    total_value_usdt = 0.0
    for asset, amount in current_balances.items():
        if asset == 'USDT':
            total_value_usdt += amount
        else:
            price = current_prices.get(f"{asset}/USDT", 0)
            total_value_usdt += amount * price

    if total_value_usdt == 0:
        return []

    trades = []
    
    # 2. Calculate Target Value for each asset
    # structure: {'BTC': 5000.0, 'ETH': 5000.0} (in USDT value)
    target_values = {}
    for asset, pct in target_allocations.items():
        target_values[asset] = total_value_usdt * pct

    # 3. Calculate Delta
    # We loop through ALL assets (targets + current holdings)
    all_assets = set(current_balances.keys()) | set(target_allocations.keys())
    
    for asset in all_assets:
        if asset == 'USDT':
            continue # We don't trade USDT for USDT
            
        current_amt = current_balances.get(asset, 0)
        current_price = current_prices.get(f"{asset}/USDT", 0)
        
        if current_price == 0:
            continue # Can't calculate value if no price
            
        current_val = current_amt * current_price
        target_val = target_values.get(asset, 0)
        
        diff_usdt = target_val - current_val
        
        # 4. Generate Trade Action
        # Threshold: Don't trade if the difference is less than $10 (dust)
        if abs(diff_usdt) > 10:
            amount_coin = abs(diff_usdt) / current_price
            action = "BUY" if diff_usdt > 0 else "SELL"
            
            trades.append({
                "action": action,
                "asset": asset,
                "amount": round(amount_coin, 6), # Round to 6 decimals
                "value_usdt": round(abs(diff_usdt), 2)
            })
            
    return trades