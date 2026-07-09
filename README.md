[![Ask DeepWiki](https://deepwiki.com/badge.svg)](https://deepwiki.com/Qoyyuum/mcp-metatrader5-server)

[![MseeP.ai Security Assessment Badge](https://mseep.net/pr/qoyyuum-mcp-metatrader5-server-badge.png)](https://mseep.ai/app/qoyyuum-mcp-metatrader5-server)

[![codecov](https://codecov.io/github/Qoyyuum/mcp-metatrader5-server/graph/badge.svg?token=SRECTEZUAR)](https://codecov.io/github/Qoyyuum/mcp-metatrader5-server)

[![PyPI version](https://badge.fury.io/py/mcp-metatrader5-server.svg)](https://pypi.org/project/mcp-metatrader5-server/)

# MetaTrader 5 MCP Server

A Model Context Protocol (MCP) server for MetaTrader 5, allowing AI assistants to interact with the MetaTrader 5 platform for trading and market data analysis. [Documentation](https://mcp-metatrader5-server.readthedocs.io)

## Features

- Connect to MetaTrader 5 terminal
- Access market data (symbols, rates, ticks)
- Place and manage trades
- Analyze trading history
- Integrate with AI assistants through the Model Context Protocol
- Run separate full-access and read-only market-data MCP entrypoints

## Installation

### From PyPI 

```bash
uvx --from mcp-metatrader5-server mt5mcp
uvx --from mcp-metatrader5-server mt5mcp-readonly
```

### From Source

```bash
git clone https://github.com/Qoyyuum/mcp-metatrader5-server.git
cd mcp-metatrader5-server
uv sync
uv run mt5mcp
uv run mt5mcp-readonly
```

## Requirements

- **uv** (recommended) or pip
- **Python 3.12 or higher**
- **MetaTrader 5 terminal** installed on Windows
- **MetaTrader 5 account** (demo or real)

## Usage

### Entrypoints

This package provides two MCP entrypoints:

- `mt5mcp` / `mt5mcp-full`: full MT5 control surface for trusted local clients. It includes login, account, positions, order checking, order sending, and position closing tools.
- `mt5mcp-readonly`: read-only market-data surface for ChatGPT-style clients. It only exposes symbol, tick, rate, and version tools. It does not expose login, account, positions, orders, order checking, order sending, position closing, symbol selection, shutdown, or reconnect tools.

The full entrypoint keeps existing behavior. The read-only entrypoint is the recommended ChatGPT app/MCP entrypoint because every exposed tool is annotated with ChatGPT-compatible read-only metadata.

### Quick Start

Both entrypoints run in **stdio mode** by default for MCP clients like Claude Desktop:

```bash
uv run mt5mcp
uv run mt5mcp-readonly
```

### Development Mode (HTTP)

For testing with HTTP transport or running both servers on a Windows VPS, create a `.env` file:

```env
# Full-access server
MT5_MCP_TRANSPORT=http
MT5_MCP_HOST=127.0.0.1
MT5_MCP_PORT=8000

# Read-only market-data server
MT5_READONLY_MCP_TRANSPORT=http
MT5_READONLY_MCP_HOST=127.0.0.1
MT5_READONLY_MCP_PORT=8001
```

Then run each entrypoint in its own terminal or service:

```bash
uv run mt5mcp
uv run mt5mcp-readonly
```

The full server will start at http://127.0.0.1:8000 and the read-only server will start at http://127.0.0.1:8001.

### Windows VPS Deployment

Recommended layout:

1. Install and log in to MetaTrader 5 on the Windows VPS.
2. Add required symbols to MT5 Market Watch before using the read-only server. The read-only entrypoint intentionally does not expose `symbol_select`.
3. Start `mt5mcp-readonly` for ChatGPT or other low-risk clients.
4. Start `mt5mcp` or `mt5mcp-full` only for trusted clients that are allowed to access account and trading tools.
5. If MT5 auto-detection is not reliable, set `MT5_PATH` or `MT5_TERMINAL_PATH` to the terminal executable path.

Example PowerShell session:

```powershell
$env:MT5_PATH = "C:\Program Files\MetaTrader 5\terminal64.exe"

$env:MT5_MCP_TRANSPORT = "http"
$env:MT5_MCP_HOST = "127.0.0.1"
$env:MT5_MCP_PORT = "8000"
uv run mt5mcp-full
```

In a second PowerShell session:

```powershell
$env:MT5_PATH = "C:\Program Files\MetaTrader 5\terminal64.exe"

$env:MT5_READONLY_MCP_TRANSPORT = "http"
$env:MT5_READONLY_MCP_HOST = "127.0.0.1"
$env:MT5_READONLY_MCP_PORT = "8001"
uv run mt5mcp-readonly
```

For public ChatGPT access, put only the read-only server behind your HTTPS reverse proxy or tunnel. Keep the full-access server private or restricted to trusted client networks.

### Installing for MCP Clients

#### Method 1: Using `uvx` (Simplest - No Installation Required) ⭐

Add this configuration to your MCP client's config file:

**For Claude Desktop** (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "mcp-metatrader5-server": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Qoyyuum/mcp-metatrader5-server",
        "mt5mcp"
      ]
    }
  }
}
```

For ChatGPT-style clients, use the read-only command:

```json
{
  "mcpServers": {
    "mcp-metatrader5-market-data": {
      "command": "uvx",
      "args": [
        "--from",
        "git+https://github.com/Qoyyuum/mcp-metatrader5-server",
        "mt5mcp-readonly"
      ]
    }
  }
}
```

#### Method 2: Using FastMCP Install (Recommended)

```bash
git clone https://github.com/Qoyyuum/mcp-metatrader5-server
cd mcp-metatrader5-server
```

After git cloning the repo, run the following commands:

For MCP JSON format

```bash
uv run fastmcp install mcp-json src/mcp_mt5/main.py
uv run fastmcp install mcp-json src/mcp_mt5/read_only.py
```

For Claude Desktop

```bash
uv run fastmcp install claude-desktop src/mcp_mt5/main.py
uv run fastmcp install claude-desktop src/mcp_mt5/read_only.py
```

For Claude Code

```bash
uv run fastmcp install claude-code src/mcp_mt5/main.py
```

For Cursor

```bash
uv run fastmcp install cursor src/mcp_mt5/main.py
```

For Gemini CLI

```bash
uv run fastmcp install gemini-cli src/mcp_mt5/main.py
```

Use `src/mcp_mt5/read_only.py` instead of `src/mcp_mt5/main.py` when installing the read-only entrypoint for any client.


#### Method 3: Manual Configuration

Add this to your `claude_desktop_config.json` or whatever LLM config file:

```json
{
  "mcpServers": {
    "mcp-metatrader5-server": {
      "command": "uvx",
      "args": [
        "--from",
        "mcp-metatrader5-server",
        "mt5mcp"
      ]
    }
  }
}
```

Read-only manual configuration:

```json
{
  "mcpServers": {
    "mcp-metatrader5-market-data": {
      "command": "uvx",
      "args": [
        "--from",
        "mcp-metatrader5-server",
        "mt5mcp-readonly"
      ]
    }
  }
}
```

## API Reference

### Read-only Market Data Entrypoint

`mt5mcp-readonly` exposes only:

- `get_version()`: Get MT5 version
- `get_symbols()`: Get all available symbols
- `get_symbols_by_group(group)`: Get symbols by group
- `get_symbol_info(symbol)`: Get information about a specific symbol
- `get_symbol_info_tick(symbol)`: Get the latest tick for a symbol already visible in Market Watch
- `copy_rates_from_pos(symbol, timeframe, start_pos, count)`: Get bars from a specific position
- `copy_rates_from_date(symbol, timeframe, date_from, count)`: Get bars from a specific date
- `copy_rates_range(symbol, timeframe, date_from, date_to)`: Get bars within a date range
- `copy_ticks_from_pos(symbol, start_time, count, flags)`: Get ticks from a specific time
- `copy_ticks_from_date(symbol, date_from, count, flags)`: Get ticks from a specific date
- `copy_ticks_range(symbol, date_from, date_to, flags)`: Get ticks within a date range

It marks every exposed tool with read-only MCP annotations:

- `readOnlyHint: true`
- `destructiveHint: false`
- `idempotentHint: true`
- `openWorldHint: true`

### Full Entrypoint

#### Connection Management

- `reconnect()`: Optional manual reconnect helper; most tools auto-initialize MT5
- `login(account, password, server)`: Log in to a trading account
- `shutdown()`: Close the connection to the MT5 terminal

#### Market Data Functions

- `get_symbols()`: Get all available symbols
- `get_symbols_by_group(group)`: Get symbols by group
- `get_symbol_info(symbol)`: Get information about a specific symbol
- `get_symbol_info_tick(symbol)`: Get the latest tick for a symbol
- `copy_rates_from_pos(symbol, timeframe, start_pos, count)`: Get bars from a specific position
- `copy_rates_from_date(symbol, timeframe, date_from, count)`: Get bars from a specific date
- `copy_rates_range(symbol, timeframe, date_from, date_to)`: Get bars within a date range
- `copy_ticks_from_pos(symbol, start_pos, count)`: Get ticks from a specific position
- `copy_ticks_from_date(symbol, date_from, count)`: Get ticks from a specific date
- `copy_ticks_range(symbol, date_from, date_to)`: Get ticks within a date range

#### Trading Functions

- `order_send(request)`: Send an order to the trade server
- `order_check(request)`: Check if an order can be placed with the specified parameters
- `positions_get(symbol, group)`: Get open positions
- `positions_get_by_ticket(ticket)`: Get an open position by its ticket
- `close_position(ticket, deviation, magic, comment, type_filling)`: Close an open position by ticket
- `orders_get(symbol, group)`: Get active orders
- `orders_get_by_ticket(ticket)`: Get an active order by its ticket
- `history_orders_get(symbol, group, ticket, position, from_date, to_date)`: Get orders from history
- `history_deals_get(symbol, group, ticket, position, from_date, to_date)`: Get deals from history

## Example Workflows

### Connecting and Getting Market Data

```python
# Optional: log in if the terminal is not already logged in
login(account=123456, password="your_password", server="your_server")

# Get available symbols
symbols = get_symbols()

# Get recent price data for EURUSD
rates = copy_rates_from_pos(symbol="EURUSD", timeframe=15, start_pos=0, count=100)

# Shut down the connection
shutdown()
```

### Placing a Trade

```python
# Optional: log in if the terminal is not already logged in
login(account=123456, password="your_password", server="your_server")

# Create an order request
request = OrderRequest(
    action=mt5.TRADE_ACTION_DEAL,
    symbol="EURUSD",
    volume=0.1,
    type=mt5.ORDER_TYPE_BUY,
    price=mt5.symbol_info_tick("EURUSD").ask,
    deviation=20,
    magic=123456,
    comment="Buy order",
    type_time=mt5.ORDER_TIME_GTC,
    type_filling=mt5.ORDER_FILLING_IOC
)

# Send the order
result = order_send(request)

# Shut down the connection
shutdown()
```

## Resources

The server provides the following resources to help AI assistants understand how to use the MetaTrader 5 API:

- `mt5://getting_started`: Basic workflow for using the MetaTrader 5 API
- `mt5://trading_guide`: Guide for placing and managing trades
- `mt5://market_data_guide`: Guide for accessing and analyzing market data
- `mt5://order_types`: Information about order types
- `mt5://order_filling_types`: Information about order filling types
- `mt5://order_time_types`: Information about order time types
- `mt5://trade_actions`: Information about trade request actions

## Prompts

The server provides the following prompts to help AI assistants interact with users:

- `connect_to_mt5(account, password, server)`: Connect to MetaTrader 5 and log in
- `analyze_market_data(symbol, timeframe)`: Analyze market data for a specific symbol
- `place_trade(symbol, order_type, volume)`: Place a trade for a specific symbol
- `manage_positions()`: Manage open positions
- `analyze_trading_history(days)`: Analyze trading history

## Development

### Project Structure

```
mcp-metatrader5-server/
├── src/
│   └── mcp_mt5/
│       ├── __init__.py      # Entry point with main()
│       ├── main.py          # FastMCP server with all tools
│       ├── read_only.py     # Read-only market-data MCP server
│       └── test_client.py   # Test client for development
├── docs/
│   ├── getting_started.md
│   ├── market_data_guide.md
│   ├── trading_guide.md
│   └── publishing.md
├── .env                     # Environment configuration (create from .env.example)
├── README.md
├── pyproject.toml           # Project metadata (using hatchling)
└── uv.lock                  # Dependency lock file
```

### Building the Package

Using uv (recommended):

```bash
uv build
```

This will create wheel and source distributions in the `dist/` directory.

### Publishing to PyPI

Using uv:

```bash
# Build first
uv build

# Publish to PyPI
uv publish

# Or publish to TestPyPI first
uv publish --publish-url https://test.pypi.org/legacy/
```

## License

MIT

## Acknowledgements

- [MetaQuotes](https://www.metaquotes.net/) for the MetaTrader 5 platform
- [FastMCP](https://github.com/jlowin/fastmcp) for the MCP server implementation
