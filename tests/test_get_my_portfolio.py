import json
import sys
import os

# 1. Add 'src' to the Python path so we can import from it
# (This fixes the "ModuleNotFoundError" you saw earlier)
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

# 2. Import the function you want to test
from exchanges.client import fetch_account_balance

def run_test():
    print("--- Connecting to Exchange ---")
    
    # 3. Call the function
    data = fetch_account_balance()
    
    # 4. Print the raw JSON nicely
    print(json.dumps(data, indent=4))
    
    print("------------------------------")

if __name__ == "__main__":
    run_test()