
import pytest
from unittest.mock import MagicMock, AsyncMock

from src.n8n_mcp.client import N8nApiClient, WorkflowModel

@pytest.fixture
def mock_settings():
    """Fixture for mock settings."""
    settings = MagicMock()
    settings.n8n.base_url = "https://test.app.n8n.cloud"
    settings.n8n.api_key = "test-api-key"
    settings.n8n.timeout = 30
    settings.n8n.max_retries = 3
    settings.performance.cache_ttl = 300
    return settings

@pytest.fixture
def mock_workflow_data():
    """Fixture for mock workflow data."""
    return {
        "name": "Test Workflow",
        "nodes": [{"name": "Start"}],
        "connections": {},
        "active": False,
    }

@pytest.fixture
def mock_workflow(mock_workflow_data):
    """Fixture for a mock WorkflowModel instance."""
    return WorkflowModel(**mock_workflow_data)

@pytest.fixture
def mock_api_response_workflow():
    """Fixture for a mock API response for a single workflow."""
    return {
        "id": "test-workflow-id",
        "name": "Test Workflow",
        "nodes": [{"name": "Start"}],
        "connections": {},
        "active": False,
        "tags": [],
    }

@pytest.fixture
def mock_api_response_workflows_list():
    """Fixture for a mock API response for a list of workflows."""
    return {
        "data": [
            {
                "id": "workflow-1",
                "name": "Test Workflow 1",
                "nodes": [],
                "connections": {},
                "active": True,
                "tags": [],
            },
            {
                "id": "workflow-2",
                "name": "Test Workflow 2",
                "nodes": [],
                "connections": {},
                "active": False,
                "tags": [],
            },
        ]
    }

@pytest.fixture
def mock_n8n_client(mock_settings):
    """Fixture for a mocked N8nApiClient."""
    client = N8nApiClient(
        base_url=mock_settings.n8n.base_url,
        api_key=mock_settings.n8n.api_key,
    )
    client._client = AsyncMock()
    return client
