import sys
import os
import json

# --- 1. Path Setup (The Magic) ---
# This tells Python: "Look for code in the folder one level up, inside 'src'"
current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.append(os.path.join(root_dir, "src"))

# --- 2. Imports ---
from exchanges.client import fetch_account_balance, fetch_price
from logic.rebalance_by_percentage import calculate_rebalance_plan

def run_test():
    print("--- 1. Defining Target ---")
    # Let's pretend we want a simple split
    targets = {"BTC": 0.5, "ETH": 0.5}
    print(f"Target: {targets}")

    print("\n--- 2. Fetching Real Balances ---")
    balances = fetch_account_balance()
    
    if "Error" in str(balances):
        print(f"CRITICAL ERROR: {balances}")
        return

    # Just for the test, let's filter out tiny 'dust' so we don't spam the API 
    # (Optional: Remove this block if you want to test the FULL huge list)
    clean_balances = {k: v for k, v in balances.items() if v > 0.0001}
    print(f"Found {len(clean_balances)} assets with balance > 0.0001")

    print("\n--- 3. Fetching Prices (This might take a moment) ---")
    # We need prices for everything we own + everything we want
    needed_assets = set(clean_balances.keys()) | set(targets.keys())
    
    current_prices = {}
    print(f"Fetching prices for {len(needed_assets)} assets...")
    
    for asset in needed_assets:
        if asset == "USDT":
            current_prices["USDT/USDT"] = 1.0
            continue
            
        # Print a dot so you know it's working and not frozen
        print(f".", end="", flush=True) 
        
        symbol = f"{asset.upper()}/USDT"
        price = fetch_price(symbol)
        
        if isinstance(price, (int, float)):
            current_prices[symbol] = price
    
    print("\nPrices fetched!")

    print("\n--- 4. Running The Logic ---")
    trades = calculate_rebalance_plan(clean_balances, current_prices, targets)

    print("\n" + "="*30)
    print("     REBALANCE PLAN RESULT     ")
    print("="*30)
    
    if not trades:
        print("No trades needed.")
    
    for trade in trades:
        print(f"{trade['action']} {trade['asset']}:")
        print(f"   Amount: {trade['amount']}")
        print(f"   Value:  ${trade['value_usdt']}")
        print("-" * 20)

if __name__ == "__main__":
    run_test()