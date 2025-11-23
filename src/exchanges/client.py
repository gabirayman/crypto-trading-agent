import ccxt.pro as ccxt
import ccxt
import os
from dotenv import load_dotenv
from config_manager import get_relevant_coins

# Load the keys from the .env file
load_dotenv()

def get_exchange():
    """
    Creates and authenticates the exchange connection.
    """
    exchange_id = os.getenv("EXCHANGE_ID", "binance")
    
    # This finds the class (e.g., ccxt.binance) based on the string name
    exchange_class = getattr(ccxt, exchange_id)
    
    # Initialize the exchange with keys
    exchange = exchange_class({
        'apiKey': os.getenv("EXCHANGE_API_KEY"),
        'secret': os.getenv("EXCHANGE_SECRET"),
        'enableRateLimit': True,  # Essential to avoid bans
    })
    
    # If SANDBOX_MODE is True in .env, use the Testnet (Fake Money)
    if os.getenv("SANDBOX_MODE") == "True":
        exchange.set_sandbox_mode(True)
        
    return exchange

def fetch_price(symbol: str):
    """
    Fetches the current price of a symbol (e.g., 'BTC/USDT').
    """
    exchange = get_exchange()
    try:
        ticker = exchange.fetch_ticker(symbol)
        return ticker['last']
    except Exception as e:
        return f"Error: {str(e)}"


def fetch_account_balance():
    """
    Fetches raw balances and immediately filters them using the Config rules.
    """
    exchange = get_exchange()
    try:
        # 1. Get RAW data (All 450+ coins)
        raw_data = exchange.fetch_balance()
        total_balances = raw_data['total']
        
        # 2. Apply the "Lens" (The Config Filter)
        # This replaces all your manual "if amount > 0" loops
        clean_balances = get_relevant_coins(total_balances)
        
        # Ensure USDT is always visible if we have it (optional safety)
        # if 'USDT' in total_balances and 'USDT' not in clean_balances:
        #      if not load_config().get("sub_wallet_assets"): # Only if whitelist is empty
        #          clean_balances['USDT'] = total_balances['USDT']

        return clean_balances

    except Exception as e:
        return f"Error: {str(e)}"

def execute_order(symbol: str, side: str, amount: float):
    """
    Executes a real market order.
    Args:
        symbol: "BTC/USDT"
        side: "buy" or "sell"
        amount: 0.001 (The quantity of the coin, NOT the USD value)
    """
    exchange = get_exchange()
    try:
        # 1. Guard Clause: Don't trade dust
        # Most exchanges reject orders < $5-$10
        # We rely on the manager to check this, but a safety net is good.
        if amount <= 0:
            return {"status": "skipped", "reason": "Amount is zero or negative"}

        # 2. Create the Order
        # 'market' means execute immediately at current price
        order = exchange.create_order(symbol, 'market', side, amount)
        
        return {
            "status": "success",
            "id": order.get('id'),
            "filled": order.get('filled'),
            "price": order.get('average') or order.get('price')
        }

    except Exception as e:
        return {"status": "failed", "error": str(e)}

