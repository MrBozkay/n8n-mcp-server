import pytest
import httpx
from unittest.mock import AsyncMock, patch
from src.n8n_mcp.client import N8nApiClient, N8nApiError, WorkflowModel

@pytest.fixture
def client():
    """Fixture for N8nApiClient."""
    return N8nApiClient(base_url="https://test.n8n.cloud", api_key="test_api_key")

@pytest.mark.asyncio
async def test_create_workflow_success(client: N8nApiClient, mocker: AsyncMock):
    """Test successful workflow creation."""
    mock_response = {
        "id": "123",
        "name": "Test Workflow",
        "active": False,
        "nodes": [],
        "connections": {},
    }
    mocker.patch.object(client, '_make_request', return_value=mock_response)

    workflow_data = WorkflowModel(name="Test Workflow")
    created_workflow = await client.create_workflow(workflow_data)

    client._make_request.assert_called_once_with(
        "POST", "/workflows", data=workflow_data.model_dump(exclude_unset=True, exclude_none=True)
    )
    assert created_workflow.id == "123"
    assert created_workflow.name == "Test Workflow"

@pytest.mark.asyncio
async def test_get_workflow_not_found(client: N8nApiClient, mocker: AsyncMock):
    """Test getting a workflow that does not exist."""
    mocker.patch.object(client, '_make_request', side_effect=N8nApiError("Not Found", status_code=404))

    workflow = await client.get_workflow("non_existent_id")

    client._make_request.assert_called_once_with(
        "GET", "/workflows/non_existent_id", use_cache=True
    )
    assert workflow is None

@pytest.mark.asyncio
async def test_make_request_retry(client: N8nApiClient, mocker: AsyncMock):
    """Test the retry mechanism in _make_request."""
    mocker.patch.object(client.client, 'request', side_effect=[
        httpx.TimeoutException("Timeout!"),
        AsyncMock(status_code=200, json=lambda: {"status": "success"})
    ])
    
    # We need to patch the asyncio.sleep to avoid waiting in tests
    mocker.patch('asyncio.sleep', return_value=None)

    response = await client._make_request("GET", "/test")

    assert client.client.request.call_count == 2
    assert response == {"status": "success"}