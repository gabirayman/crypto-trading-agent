import json
import sys
import os

# 1. Add 'src' to the Python path so we can import from it
sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))

# 2. Import the function you want to test
from exchanges.client import fetch_account_balance
from config_manager import update_sub_wallet

def run_test():
    print("--- Connecting to Exchange ---")

    # lets make a subwallet for a couple of coins
    update_sub_wallet(["BTC", "ETH", "USDT", "SOL", "ADA", "XRP"])

    
    # 3. Call the function
    data = fetch_account_balance()
    
    # 4. Print the raw JSON nicely
    print(json.dumps(data, indent=4))
    
    print("------------------------------")

    update_sub_wallet([])  # reset sub-wallet

if __name__ == "__main__":
    run_test()

# to run this test file, use:
# uv run tests/test_get_my_portfolio.py