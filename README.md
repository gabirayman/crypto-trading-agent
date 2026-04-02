# 🤖 Autonomous Finance Agent (Crypto MCP)

[![Python](https://img.shields.io/badge/Python-3.12+-blue.svg)](https://www.python.org/)
[![MCP](https://img.shields.io/badge/MCP-FastMCP-green.svg)](https://github.com/fastmcp/fastmcp)
[![CCXT](https://img.shields.io/badge/CCXT-Exchange%20Integration-orange.svg)](https://github.com/ccxt/ccxt)

An intelligent Model Context Protocol (MCP) server that empowers Large Language Models (LLMs) to natively analyze, manage, and rebalance cryptocurrency portfolios across major exchanges.

Designed with agentic workflows in mind, this server exposes clean, domain-specific tools to any compatible AI assistant, allowing them to function as fully autonomous financial analysts and traders.

---

## 🌟 Key Features

*   **Agentic Portfolio Rebalancing:** Calculate target allocations and dynamically plan intelligent trade execution (executing Sells *before* Buys to manage USDT liquidity).
*   **Universal Exchange Support:** Powered by `ccxt`, enabling seamless integration with Binance, Coinbase, Kraken, and over 100+ other global exchanges.
*   **Sandbox & Safe Execution:** Built-in safeguards including Sandbox mode (Testnet execution), dust-trade prevention, and minimum balance thresholds.
*   **Smart Sub-Wallets:** Configure specific asset allowlists and sub-wallets to prevent the AI from interacting with unauthorized or highly volatile tokens.
*   **Real-time Market Context:** Fetch live crypto prices and total portfolio valuations in USDT to empower LLM decision-making.

## 🛠️ Technology Stack

*   **Language:** Python 3.12+
*   **Package Management:** `uv` for lightning-fast dependency resolution
*   **Protocol Layer:** `fastmcp` (Model Context Protocol Implementation)
*   **Finance Infrastructure:** `ccxt` (CryptoCurrency eXchange Trading Library)

## 🧰 Available LLM Tools

This server exposes the following capabilities directly to the LLM context:

*   `get_crypto_price(asset)`: Fetches the current live price.
*   `get_my_portfolio()`: Retrieves all non-zero balance holdings.
*   `get_total_portfolio_value()`: Calculates overall portfolio health and total value in USDT.
*   `plan_portfolio_rebalance(target_percentages)`: Computes the precise trades needed to achieve target asset allocations (e.g., `{"BTC": 0.5, "ETH": 0.5}`).
*   `execute_trading_plan(trades_json)`: Autonomously executes a compiled list of trades, ordered intelligently.
*   `trade_single(trade_json)`: Executes an individual buy/sell market order.
*   `create_sub_wallet(coins_list)`: Creates a restricted configuration for specific assets.
*   `set_min_balance_threshold(threshold_value)`: Filters out dust from portfolio analytics.

## 🔒 Configuration & Safety

The project places a strong emphasis on safety before autonomous execution. Configure your `.env` file:

```env
EXCHANGE_ID=binance
EXCHANGE_API_KEY=your_api_key
EXCHANGE_SECRET=your_secret_key
SANDBOX_MODE=True # Ensures the LLM executes trades ONLY on an exchange's Testnet
```

## 🚀 Getting Started

1. **Install dependencies:**
   Ensure you have [uv](https://docs.astral.sh/uv/) installed.
   ```bash
   uv sync
   ```
2. **Configure your environment:** 
   Copy `.env.example` to `.env` and fill in your exchange credentials. It is highly recommended to set `SANDBOX_MODE=True` for safe iteration.
3. **Connect to Claude Desktop:**
   This project is designed to be used as an MCP server with Claude Desktop rather than run directly in the terminal. To use it, follow the official MCP documentation to connect it as a local tool:
   [Connect Local Servers (MCP Docs)](https://modelcontextprotocol.io/docs/develop/connect-local-servers)

## 🧠 System Architecture

The project follows a clean, modular architecture separating concerns between the LLM integration layer and the exchange execution layer:
*   **`src/server.py`:** The presentation/MCP layer. Defines MCP tools, parses textual LLM inputs into JSON, formats outputs, and handles validation.
*   **`src/logic/`:** The business logic domain. Handles complex math like generating rebalancing ratios, fetching optimal batch prices, and sequentially ordering trade executions.
*   **`src/exchanges/client.py`:** The infrastructure mapping layer. Abstracting exchange interactions and API connections via CCXT.
*   **`config_manager.py`:** Centralized state management for the agent's safe sub-wallet boundaries and dust-filtering rules.
