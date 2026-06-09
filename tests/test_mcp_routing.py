import pytest
import asyncio
from unittest.mock import MagicMock, patch, AsyncMock
from magda_agent.skills.mcp_client import MCPClient

@pytest.mark.asyncio
async def test_mcp_server_routing():
    """Test that server-prefixed tool names are correctly routed to the server URL."""
    client = MCPClient(timeout=1.0)
    client.register_server("weather_service", "http://weather-api.local/rpc")

    assert client.has_tool("weather_service:get_forecast") is True

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "jsonrpc": "2.0",
            "result": "Sunny",
            "id": "1"
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        result = await client.execute_tool("weather_service:get_forecast", city="Berlin")

        assert result == "Sunny"
        # Verify the call went to the server URL with the correct method (stripped of prefix)
        args, kwargs = mock_post.call_args
        assert args[0] == "http://weather-api.local/rpc"
        assert kwargs["json"]["method"] == "get_forecast"
        assert kwargs["json"]["params"] == {"city": "Berlin"}

@pytest.mark.asyncio
async def test_mcp_tool_precedence():
    """Test that individually registered tools take precedence over server prefixes."""
    client = MCPClient(timeout=1.0)
    # Register a server
    client.register_server("tools", "http://server-url/rpc")
    # Register an individual tool with the same name as a prefixed tool
    client.register_remote_tool("tools:special_tool", {"url": "http://special-url/rpc"})

    assert client.has_tool("tools:special_tool") is True

    with patch("httpx.AsyncClient.post") as mock_post:
        mock_response = MagicMock()
        mock_response.json.return_value = {"jsonrpc": "2.0", "result": "Special Result", "id": "1"}
        mock_post.return_value = mock_response

        result = await client.execute_tool("tools:special_tool")

        assert result == "Special Result"
        # Should go to special-url, and method should be the full name as it's an individual tool
        args, kwargs = mock_post.call_args
        assert args[0] == "http://special-url/rpc"
        assert kwargs["json"]["method"] == "tools:special_tool"

@pytest.mark.asyncio
async def test_mcp_routing_errors():
    """Test error cases for missing servers or malformed names."""
    client = MCPClient(timeout=1.0)
    client.register_server("known", "http://known/rpc")

    # Missing server
    result = await client.execute_tool("unknown:tool")
    assert "Error: MCP server prefix 'unknown' not found" in result

    # Missing tool (not in registered_tools and no prefix)
    result = await client.execute_tool("some_tool")
    assert "Error: Remote MCP skill 'some_tool' not found" in result

@pytest.mark.asyncio
async def test_mcp_server_registration():
    """Test server registration."""
    client = MCPClient()
    client.register_server("srv", "http://srv")
    assert client.registered_servers["srv"] == "http://srv"
    assert client.has_tool("srv:any") is True
    assert client.has_tool("other:any") is False
