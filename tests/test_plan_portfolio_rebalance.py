import sys
import os
import json

# --- 1. Path Setup (The Magic) ---
# This tells Python: "Look for code in the folder one level up, inside 'src'"
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# --- 2. Imports ---
from exchanges.client import fetch_account_balance, fetch_price
from logic.rebalance_by_percentage import calculate_rebalance_plan
from logic.portfolio_manager import generate_rebalance_plan
from config_manager import update_sub_wallet

def run_test():
    print("--- 1. Defining Target ---")
    # Let's pretend we want a simple split
    targets = {"BTC": 0.5, "ETH": 0.25, "USDT": 0.25}
    print(f"Target: {targets}")

    # lets make a subwallet for a couple of coins
    update_sub_wallet(["BTC", "ETH", "USDT", "SOL", "ADA", "XRP"])


    print("\n--- 2. Fetching Real Balances ---")
    trades = generate_rebalance_plan(targets)
    
    if "Error" in str(trades):
        print(f"Error during rebalance plan generation")
        update_sub_wallet([])  # reset sub-wallet
        return

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
    
    update_sub_wallet([])  # reset sub-wallet

if __name__ == "__main__":
    run_test()

# to run this test file, use:
# uv run tests/test_plan_portfolio_rebalance.py