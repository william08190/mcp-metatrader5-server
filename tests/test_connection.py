"""Unit tests for MT5 connection management."""

from unittest.mock import patch

import pytest
from fastmcp import Client

from mcp_mt5.main import initialize, mcp


@pytest.mark.unit
class TestConnectionManagement:
    """Test MT5 connection initialization and management."""

    @patch("mcp_mt5.main.mt5")
    def test_initialize_success(self, mock_mt5):
        """Test successful MT5 initialization."""
        mock_mt5.initialize.return_value = True

        result = initialize(path="")

        assert result is True
        mock_mt5.initialize.assert_called_once_with(path="")

    @patch("mcp_mt5.main.mt5")
    def test_initialize_default_path(self, mock_mt5):
        """Test initialize defaults to MT5 auto-detection."""
        mock_mt5.initialize.return_value = True

        result = initialize()

        assert result is True
        mock_mt5.initialize.assert_called_once_with(path="")

    @patch("mcp_mt5.main.mt5")
    def test_initialize_failure(self, mock_mt5):
        """Test failed MT5 initialization."""
        mock_mt5.initialize.return_value = False
        mock_mt5.last_error.return_value = (1, "Initialization failed")

        result = initialize(path="C:\\Invalid\\Path\\terminal64.exe")

        assert result is False
        mock_mt5.initialize.assert_called_once()
        mock_mt5.last_error.assert_called_once()

    async def test_initialize_is_not_exposed_as_mcp_tool(self):
        """Path-taking initialize is kept out of the MCP tool list."""
        async with Client(mcp) as client:
            tools = await client.list_tools()

        listed_tools = tools.tools if hasattr(tools, "tools") else tools
        tool_names = {tool.name for tool in listed_tools}
        assert "initialize" not in tool_names
        assert "reconnect" in tool_names

    @patch("mcp_mt5.main.mt5")
    async def test_reconnect_tool_uses_server_config(self, mock_mt5, monkeypatch):
        """Reconnect uses server-side config and exposes no path argument."""
        monkeypatch.setenv("MT5_PATH", "C:\\MT5\\terminal64.exe")
        mock_mt5.initialize.return_value = True

        async with Client(mcp) as client:
            result = await client.call_tool("reconnect", {})

        assert result.data is True
        mock_mt5.initialize.assert_called_once_with(path="C:\\MT5\\terminal64.exe")

    @patch("mcp_mt5.main.mt5")
    async def test_shutdown(self, mock_mt5):
        """Test MT5 shutdown."""
        async with Client(mcp) as client:
            result = await client.call_tool("shutdown", {})

        assert result.data is True
        mock_mt5.shutdown.assert_called_once()

    @patch("mcp_mt5.main.mt5")
    async def test_login_success(self, mock_mt5):
        """Test successful login."""
        mock_mt5.login.return_value = True

        async with Client(mcp) as client:
            result = await client.call_tool(
                "login", {"login": 123456, "password": "test_pass", "server": "TestServer"}
            )

        assert result.data is True
        mock_mt5.login.assert_called_once_with(
            login=123456, password="test_pass", server="TestServer"
        )

    @patch("mcp_mt5.main.mt5")
    async def test_login_failure(self, mock_mt5):
        """Test failed login."""
        mock_mt5.login.return_value = False
        mock_mt5.last_error.return_value = (2, "Invalid credentials")

        async with Client(mcp) as client:
            result = await client.call_tool(
                "login", {"login": 123456, "password": "wrong_pass", "server": "TestServer"}
            )

        assert result.data is False
        mock_mt5.login.assert_called_once()
        mock_mt5.last_error.assert_called_once()

    @patch("mcp_mt5.main.mt5")
    async def test_get_version(self, mock_mt5):
        """Test getting MT5 version."""
        mock_mt5.version.return_value = (5, 0, 5260)

        async with Client(mcp) as client:
            result = await client.call_tool("get_version", {})

        assert result.data == {"version": 5, "build": 0, "date": 5260}
        mock_mt5.version.assert_called_once()

    @patch("mcp_mt5.main.mt5")
    async def test_get_version_failure(self, mock_mt5):
        """Test get_version when MT5 returns None."""
        mock_mt5.version.return_value = None
        mock_mt5.last_error.return_value = (3, "Not connected")

        async with Client(mcp) as client:
            with pytest.raises(Exception, match="Failed to get version"):
                await client.call_tool("get_version", {})

        mock_mt5.version.assert_called_once()
        mock_mt5.last_error.assert_called_once()

    @pytest.mark.auto_initialize
    @patch("mcp_mt5.main.mt5")
    async def test_tools_auto_initialize_before_use(self, mock_mt5):
        """Test regular tools initialize MT5 without an explicit initialize tool call."""
        mock_mt5.terminal_info.side_effect = [None, object()]
        mock_mt5.initialize.return_value = True
        mock_mt5.version.return_value = (5, 0, 5260)

        async with Client(mcp) as client:
            result = await client.call_tool("get_version", {})

        assert result.data == {"version": 5, "build": 0, "date": 5260}
        mock_mt5.initialize.assert_called_once_with(path="")
        mock_mt5.version.assert_called_once()

    @pytest.mark.auto_initialize
    @patch("mcp_mt5.main.mt5")
    async def test_auto_initialize_uses_server_env_path(self, mock_mt5, monkeypatch):
        """Test auto-initialization uses server env config instead of tool arguments."""
        monkeypatch.setenv("MT5_PATH", "C:\\MT5\\terminal64.exe")
        mock_mt5.terminal_info.side_effect = [None, object()]
        mock_mt5.initialize.return_value = True
        mock_mt5.version.return_value = (5, 0, 5260)

        async with Client(mcp) as client:
            result = await client.call_tool("get_version", {})

        assert result.data == {"version": 5, "build": 0, "date": 5260}
        mock_mt5.initialize.assert_called_once_with(path="C:\\MT5\\terminal64.exe")
        mock_mt5.version.assert_called_once()


@pytest.mark.unit
class TestConnectionParameters:
    """Test connection parameter validation."""

    @patch("mcp_mt5.main.mt5")
    def test_initialize_with_various_paths(self, mock_mt5):
        """Test initialize with different path formats."""
        mock_mt5.initialize.return_value = True

        paths = [
            "",
            "C:\\Program Files\\MetaTrader 5\\terminal64.exe",
            "C:/Program Files/MetaTrader 5/terminal64.exe",
            "D:\\MT5\\terminal64.exe",
        ]

        for path in paths:
            result = initialize(path=path)
            assert result is True

    @patch("mcp_mt5.main.mt5")
    async def test_login_with_different_servers(self, mock_mt5):
        """Test login with different server names."""
        mock_mt5.login.return_value = True

        servers = [
            "MetaQuotes-Demo",
            "Broker-Live",
            "TestServer-01",
        ]

        async with Client(mcp) as client:
            for server in servers:
                result = await client.call_tool(
                    "login", {"login": 123456, "password": "pass", "server": server}
                )
                assert result.data is True
