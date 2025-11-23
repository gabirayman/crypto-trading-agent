import json
import os
from typing import Dict, List, Any

# Path to the config file
CONFIG_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config.json")

DEFAULT_CONFIG = {
    "min_balance_threshold": 0.0001,  # Ignore really tiny dust
    "sub_wallet_assets": []           # Empty means "Allow All"
}

def load_config() -> dict:
    """Loads config or creates default if missing."""
    if not os.path.exists(CONFIG_PATH):
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG
    try:
        with open(CONFIG_PATH, 'r') as f:
            return json.load(f)
    except:
        return DEFAULT_CONFIG

def save_config(config: dict):
    with open(CONFIG_PATH, 'w') as f:
        json.dump(config, f, indent=4)

# --- The Side Function (Filter Logic) ---
def get_relevant_coins(balances: Dict[str, float]) -> Dict[str, float]:
    """
    Filters a raw balance dictionary based on the Config rules.
    1. 'sub_wallet_assets': If not empty, ONLY keep these coins.
    2. 'min_balance_threshold': ONLY keep coins >= this amount.
    """
    config = load_config()
    threshold = config.get("min_balance_threshold", 0.0)
    whitelist = config.get("sub_wallet_assets", [])
    
    # Force whitelist to uppercase for safety
    whitelist = [c.upper() for c in whitelist]
    
    filtered_balances = {}
    
    for asset, amount in balances.items():
        asset_upper = asset.upper()
        
        # Rule 1: Whitelist Check
        # If whitelist has items, AND this asset is NOT in it -> Skip it.
        if whitelist and (asset_upper not in whitelist):
            continue
            
        # Rule 2: Threshold Check
        # If amount is strictly less than threshold -> Skip it.
        if amount < threshold:
            continue
            
        # If we passed both checks, keep it.
        filtered_balances[asset] = amount
        
    return filtered_balances

# --- Helpers for Chat Tools ---
def update_sub_wallet(assets: List[str]):
    conf = load_config()
    conf["sub_wallet_assets"] = [a.upper() for a in assets]
    save_config(conf)

def set_min_threshold(val: float):
    conf = load_config()
    conf["min_balance_threshold"] = val
    save_config(conf)