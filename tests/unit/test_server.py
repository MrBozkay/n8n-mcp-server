import pytest
from unittest.mock import AsyncMock, MagicMock
from src.n8n_mcp.server import N8nMcpServer, get_tool_definitions
from src.n8n_mcp.config import Settings, N8nConfig, McpConfig, LoggingConfig, PerformanceConfig
from src.n8n_mcp.client import WorkflowModel

@pytest.fixture
def mock_settings():
    """Fixture for Settings."""
    return Settings(
        n8n=N8nConfig(base_url="https://test.n8n.cloud", api_key="test_api_key"),
        mcp=McpConfig(server_name="test-server", version="1.0.0"),
        logging=LoggingConfig(level="INFO"),
        performance=PerformanceConfig(cache_ttl=300)
    )

@pytest.fixture
async def mcp_server(mock_settings):
    """Fixture for N8nMcpServer."""
    server = N8nMcpServer(mock_settings)
    # Mock the n8n_client
    server.n8n_client = AsyncMock()
    yield server

@pytest.mark.asyncio
async def test_handle_create_workflow_success(mcp_server: N8nMcpServer):
    """Test successful workflow creation handler."""
    mcp_server.n8n_client.create_workflow.return_value = WorkflowModel(
        id="123", name="New Workflow", nodes=[], connections={}
    )

    args = {"name": "New Workflow"}
    result = await mcp_server._handle_create_workflow(args)

    mcp_server.n8n_client.create_workflow.assert_called_once()
    assert "Workflow 'New Workflow' created successfully" in result[0].text

@pytest.mark.asyncio
async def test_handle_get_workflow_not_found(mcp_server: N8nMcpServer):
    """Test get workflow handler when workflow is not found."""
    mcp_server.n8n_client.get_workflow.return_value = None

    args = {"workflow_id": "non_existent_id"}
    result = await mcp_server._handle_get_workflow(args)

    mcp_server.n8n_client.get_workflow.assert_called_once_with("non_existent_id", use_cache=True)
    assert "Workflow not found" in result[0].text

def test_get_tool_definitions():
    """Test the static tool definitions."""
    tools = get_tool_definitions()
    assert len(tools) > 0
    assert tools[0].name == "create_workflow"