import ccxt.pro as ccxt
import ccxt
import os
from dotenv import load_dotenv

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
    Fetches the user's wallet balance.
    Returns a dictionary of assets where the balance is > 0.
    """
    exchange = get_exchange()
    try:
        # This call REQUIRES valid API keys
        balance = exchange.fetch_balance()
        
        # 'total' contains the combined free and used (locked) funds
        return balance['total'] 
    except Exception as e:
        return f"Error: {str(e)}"