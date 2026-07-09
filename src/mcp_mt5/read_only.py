"""Read-only MetaTrader 5 MCP entrypoint for ChatGPT-style clients."""

import importlib
import os
from datetime import datetime
from typing import Any

from dotenv import load_dotenv
from fastmcp import FastMCP

from .main import READ_ONLY_ANNOTATIONS, READ_ONLY_META, SymbolInfo

full = importlib.import_module("mcp_mt5.main")

mcp = FastMCP(
    "MetaTrader 5 Market Data MCP Server",
    instructions="""
    This is the read-only MetaTrader 5 MCP server for ChatGPT-style clients.

    Safety boundary:
    - This entrypoint only exposes market-data and version tools.
    - It does not expose login, account, positions, orders, order_check,
      order_send, close_position, symbol_select, shutdown, or reconnect.
    - Tools may initialize or reattach to the configured MT5 terminal, but they
      must not place trades, modify orders, close positions, log in, or change
      account state.

    Server setup:
    - The MT5 terminal must already be installed, running, and logged in on the
      server host when broker access is required.
    - Symbols queried by tick/rate tools should already be visible in MT5
      Market Watch. Configure the watchlist on the server host instead of
      exposing symbol_select to ChatGPT.
    - Configure MT5_PATH or MT5_TERMINAL_PATH in the MCP server environment if
      auto-detection is not enough.
    """,
)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def get_version() -> dict[str, Any]:
    """
    Get the MetaTrader 5 version.

    Returns:
        Dict[str, Any]: Version information.
    """
    return full.get_version()


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def get_symbols() -> list[str]:
    """
    Get all available symbols from the configured MetaTrader 5 terminal.

    Returns:
        List[str]: List of symbol names.
    """
    return full.get_symbols()


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def get_symbols_by_group(group: str) -> list[str]:
    """
    Get symbols that match a specific group or pattern.

    Args:
        group: Filter for arranging a group of symbols, e.g. "*", "EUR*".

    Returns:
        List[str]: List of symbol names that match the group.
    """
    return full.get_symbols_by_group(group)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def get_symbol_info(symbol: str) -> SymbolInfo:
    """
    Get broker-provided metadata for a specific symbol.

    Args:
        symbol: Symbol name, e.g. "EURUSD", "XAUUSD".

    Returns:
        SymbolInfo: Information about the symbol.
    """
    return full.get_symbol_info(symbol)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def get_symbol_info_tick(symbol: str) -> dict[str, Any]:
    """
    Get the latest tick data for a symbol.

    The symbol must already be visible in MT5 Market Watch on the server host.
    This read-only entrypoint intentionally does not expose symbol_select.

    Args:
        symbol: Symbol name, e.g. "EURUSD", "XAUUSD", "GBPUSD".

    Returns:
        Dict[str, Any]: Latest tick data.
    """
    return full.get_symbol_info_tick(symbol)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_rates_from_pos(
    symbol: str, timeframe: int, start_pos: int, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe starting from a bar position.

    Args:
        symbol: Symbol name, e.g. "EURUSD", "GBPUSD".
        timeframe: Timeframe in minutes, e.g. 1, 5, 15, 30, 60, 240, 1440.
        start_pos: Starting position, where 0 is the most recent bar.
        count: Number of bars to retrieve.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_from_pos(symbol, timeframe, start_pos, count)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_rates_from_date(
    symbol: str, timeframe: int, date_from: datetime, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe starting from a date.

    Args:
        symbol: Symbol name.
        timeframe: Timeframe in minutes, e.g. 1, 5, 15, 30, 60, 240, 1440.
        date_from: Start date for bar retrieval.
        count: Number of bars to retrieve.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_from_date(symbol, timeframe, date_from, count)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_rates_range(
    symbol: str, timeframe: int, date_from: datetime, date_to: datetime
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe within a date range.

    Args:
        symbol: Symbol name.
        timeframe: Timeframe in minutes, e.g. 1, 5, 15, 30, 60, 240, 1440.
        date_from: Start date for bar retrieval.
        date_to: End date for bar retrieval.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_range(symbol, timeframe, date_from, date_to)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_from_pos(
    symbol: str, start_time: datetime, count: int, flags: int = full.mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol starting from an initial time.

    Args:
        symbol: Symbol name.
        start_time: Initial time for tick retrieval.
        count: Number of ticks to retrieve.
        flags: Type of requested ticks.

    Returns:
        List[Dict[str, Any]]: JSON-serializable ticks.
    """
    return full.copy_ticks_from_pos(symbol, start_time, count, flags)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_from_date(
    symbol: str, date_from: datetime, count: int, flags: int = full.mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol starting from a date.

    Args:
        symbol: Symbol name.
        date_from: Start date for tick retrieval.
        count: Number of ticks to retrieve.
        flags: Type of requested ticks.

    Returns:
        List[Dict[str, Any]]: JSON-serializable ticks.
    """
    return full.copy_ticks_from_date(symbol, date_from, count, flags)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_range(
    symbol: str, date_from: datetime, date_to: datetime, flags: int = full.mt5.COPY_TICKS_ALL
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol within a date range.

    Args:
        symbol: Symbol name.
        date_from: Start date for tick retrieval.
        date_to: End date for tick retrieval.
        flags: Type of requested ticks.

    Returns:
        List[Dict[str, Any]]: JSON-serializable ticks.
    """
    return full.copy_ticks_range(symbol, date_from, date_to, flags)


def main() -> None:
    """Entry point for the read-only MCP server CLI."""
    load_dotenv()

    transport = os.getenv("MT5_READONLY_MCP_TRANSPORT", os.getenv("MT5_MCP_TRANSPORT", "stdio"))
    if transport == "http":
        host = os.getenv("MT5_READONLY_MCP_HOST", os.getenv("MT5_MCP_HOST", "127.0.0.1"))
        port = int(os.getenv("MT5_READONLY_MCP_PORT", "8001"))
        mcp.run(transport="http", host=host, port=port)
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
