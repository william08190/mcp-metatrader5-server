"""Read-only MetaTrader 5 MCP entrypoint for ChatGPT-style clients."""

import importlib
import os
from datetime import datetime
from typing import Annotated, Any, Literal

from dotenv import load_dotenv
from fastmcp import FastMCP
from pydantic import Field

from .main import READ_ONLY_ANNOTATIONS, READ_ONLY_META, SymbolInfo

full = importlib.import_module("mcp_mt5.main")

DateTimeUTC = Annotated[
    datetime,
    Field(
        description=(
            "ISO 8601 date-time string with an explicit timezone. Use UTC with "
            "a trailing Z, for example 2026-07-09T01:00:00Z."
        ),
        examples=["2026-07-09T01:00:00Z"],
    ),
]

TickFlags = Annotated[
    Literal[-1, 1, 2],
    Field(
        description=(
            "MT5 tick filter. Use -1 for all ticks, 1 for bid/ask quote-change "
            "ticks, or 2 for trade ticks."
        ),
        examples=[-1],
    ),
]

TimeframeMinutes = Annotated[
    int,
    Field(
        description=(
            "MT5 timeframe in minutes. Common values: 1=M1, 5=M5, 15=M15, "
            "30=M30, 60=H1, 240=H4, 1440=D1, 10080=W1, 43200=MN1."
        ),
        examples=[60],
    ),
]

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
    symbol: str, timeframe: TimeframeMinutes, start_pos: int, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe starting from a bar position.

    Args:
        symbol: Symbol name, e.g. "EURUSD", "GBPUSD".
        timeframe: MT5 timeframe in minutes. Common values: 1=M1, 5=M5, 15=M15,
            30=M30, 60=H1, 240=H4, 1440=D1, 10080=W1, 43200=MN1.
        start_pos: Starting position, where 0 is the most recent bar.
        count: Number of bars to retrieve.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_from_pos(symbol, timeframe, start_pos, count)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_rates_from_date(
    symbol: str, timeframe: TimeframeMinutes, date_from: DateTimeUTC, count: int
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe starting from a date.

    Args:
        symbol: Symbol name.
        timeframe: MT5 timeframe in minutes. Common values: 1=M1, 5=M5, 15=M15,
            30=M30, 60=H1, 240=H4, 1440=D1, 10080=W1, 43200=MN1.
        date_from: Start date-time for bar retrieval. Use an ISO 8601 UTC
            string with trailing Z, for example 2026-07-09T01:00:00Z.
        count: Number of bars to retrieve.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_from_date(symbol, timeframe, date_from, count)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_rates_range(
    symbol: str,
    timeframe: TimeframeMinutes,
    date_from: DateTimeUTC,
    date_to: DateTimeUTC,
) -> list[dict[str, Any]]:
    """
    Get bars from a symbol and timeframe within a date range.

    Args:
        symbol: Symbol name.
        timeframe: MT5 timeframe in minutes. Common values: 1=M1, 5=M5, 15=M15,
            30=M30, 60=H1, 240=H4, 1440=D1, 10080=W1, 43200=MN1.
        date_from: Start date-time for bar retrieval. Use an ISO 8601 UTC
            string with trailing Z, for example 2026-07-09T01:00:00Z.
        date_to: End date-time for bar retrieval. Use an ISO 8601 UTC string
            with trailing Z, for example 2026-07-09T02:00:00Z.

    Returns:
        List[Dict[str, Any]]: JSON-serializable OHLCV bars.
    """
    return full.copy_rates_range(symbol, timeframe, date_from, date_to)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_from_pos(
    symbol: str,
    start_time: DateTimeUTC,
    count: int,
    flags: TickFlags = full.mt5.COPY_TICKS_ALL,
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol starting from an initial time.

    Args:
        symbol: Symbol name.
        start_time: Initial date-time for tick retrieval. Use an ISO 8601 UTC
            string with trailing Z, for example 2026-07-09T01:00:00Z.
        count: Number of ticks to retrieve.
        flags: MT5 tick filter. Use -1 for all ticks, 1 for bid/ask
            quote-change ticks, or 2 for trade ticks.

    Returns:
        List[Dict[str, Any]]: JSON-serializable ticks.
    """
    return full.copy_ticks_from_pos(symbol, start_time, count, flags)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_from_date(
    symbol: str,
    date_from: DateTimeUTC,
    count: int,
    flags: TickFlags = full.mt5.COPY_TICKS_ALL,
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol starting from a date.

    Args:
        symbol: Symbol name.
        date_from: Start date-time for tick retrieval. Use an ISO 8601 UTC
            string with trailing Z, for example 2026-07-09T01:00:00Z.
        count: Number of ticks to retrieve.
        flags: MT5 tick filter. Use -1 for all ticks, 1 for bid/ask
            quote-change ticks, or 2 for trade ticks.

    Returns:
        List[Dict[str, Any]]: JSON-serializable ticks.
    """
    return full.copy_ticks_from_date(symbol, date_from, count, flags)


@mcp.tool(annotations=READ_ONLY_ANNOTATIONS, meta=READ_ONLY_META)
def copy_ticks_range(
    symbol: str,
    date_from: DateTimeUTC,
    date_to: DateTimeUTC,
    flags: TickFlags = full.mt5.COPY_TICKS_ALL,
) -> list[dict[str, Any]]:
    """
    Get ticks from a symbol within a date range.

    Args:
        symbol: Symbol name.
        date_from: Start date-time for tick retrieval. Use an ISO 8601 UTC
            string with trailing Z, for example 2026-07-09T01:00:00Z.
        date_to: End date-time for tick retrieval. Use an ISO 8601 UTC string
            with trailing Z, for example 2026-07-09T02:00:00Z.
        flags: MT5 tick filter. Use -1 for all ticks, 1 for bid/ask
            quote-change ticks, or 2 for trade ticks.

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
