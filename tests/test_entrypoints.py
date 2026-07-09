"""Tests for full and read-only MCP entrypoints."""

import tomllib
from pathlib import Path

import pytest
from fastmcp import Client

from mcp_mt5.main import mcp as full_mcp
from mcp_mt5.read_only import mcp as read_only_mcp

READ_ONLY_TOOL_NAMES = {
    "get_version",
    "get_symbols",
    "get_symbols_by_group",
    "get_symbol_info",
    "get_symbol_info_tick",
    "copy_rates_from_pos",
    "copy_rates_from_date",
    "copy_rates_range",
    "copy_ticks_from_pos",
    "copy_ticks_from_date",
    "copy_ticks_range",
}


def _annotations(tool) -> dict:
    annotations = tool.annotations
    if annotations is None:
        return {}
    if hasattr(annotations, "model_dump"):
        return annotations.model_dump(exclude_none=True)
    return dict(annotations)


def _meta(tool) -> dict:
    if hasattr(tool, "model_dump"):
        data = tool.model_dump(by_alias=True)
        return data.get("_meta") or data.get("meta") or {}
    return getattr(tool, "meta", None) or {}


def _tools(result):
    return result.tools if hasattr(result, "tools") else result


@pytest.mark.unit
async def test_read_only_entrypoint_exposes_only_market_data_tools():
    async with Client(read_only_mcp) as client:
        tools = _tools(await client.list_tools())

    tool_names = {tool.name for tool in tools}

    assert tool_names == READ_ONLY_TOOL_NAMES
    assert "login" not in tool_names
    assert "get_account_info" not in tool_names
    assert "positions_get" not in tool_names
    assert "orders_get" not in tool_names
    assert "order_check" not in tool_names
    assert "order_send" not in tool_names
    assert "close_position" not in tool_names
    assert "symbol_select" not in tool_names
    assert "shutdown" not in tool_names


@pytest.mark.unit
async def test_read_only_entrypoint_tools_have_chatgpt_safe_annotations():
    async with Client(read_only_mcp) as client:
        tools = _tools(await client.list_tools())

    for tool in tools:
        annotations = _annotations(tool)
        meta = _meta(tool)

        assert annotations["readOnlyHint"] is True
        assert annotations["destructiveHint"] is False
        assert annotations["idempotentHint"] is True
        assert annotations["openWorldHint"] is True
        assert meta["openai/visibility"] == "public"
        assert meta["securitySchemes"] == [{"type": "noauth"}]


@pytest.mark.unit
async def test_full_entrypoint_keeps_trading_tools_with_risk_annotations():
    async with Client(full_mcp) as client:
        tools = _tools(await client.list_tools())

    tools_by_name = {tool.name: tool for tool in tools}

    assert "order_send" in tools_by_name
    assert "close_position" in tools_by_name
    assert "login" in tools_by_name
    assert "get_account_info" in tools_by_name

    order_send_annotations = _annotations(tools_by_name["order_send"])
    assert order_send_annotations["readOnlyHint"] is False
    assert order_send_annotations["destructiveHint"] is True
    assert order_send_annotations["idempotentHint"] is False
    assert order_send_annotations["openWorldHint"] is True

    close_position_annotations = _annotations(tools_by_name["close_position"])
    assert close_position_annotations["readOnlyHint"] is False
    assert close_position_annotations["destructiveHint"] is True

    login_annotations = _annotations(tools_by_name["login"])
    assert login_annotations["readOnlyHint"] is False
    assert login_annotations["destructiveHint"] is False
    assert login_annotations["idempotentHint"] is False

    account_annotations = _annotations(tools_by_name["get_account_info"])
    assert account_annotations["readOnlyHint"] is True
    assert account_annotations["destructiveHint"] is False


@pytest.mark.unit
def test_pyproject_exposes_full_and_read_only_console_scripts():
    pyproject_path = Path(__file__).resolve().parents[1] / "pyproject.toml"
    pyproject = tomllib.loads(pyproject_path.read_text())

    scripts = pyproject["project"]["scripts"]

    assert scripts["mt5mcp"] == "mcp_mt5:main"
    assert scripts["mt5mcp-full"] == "mcp_mt5:main"
    assert scripts["mt5mcp-readonly"] == "mcp_mt5.read_only:main"
