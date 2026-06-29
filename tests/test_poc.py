import pytest
from datetime import date


# ── Repository ────────────────────────────────────────────────────────────────

def test_repository_known_id():
    from repository.policy_repository import DocumentRepository, PolicyDocument
    repo = DocumentRepository()
    doc = repo.get_by_id("Fake_id")
    assert doc is not None
    assert isinstance(doc, PolicyDocument)
    assert doc.policy_name == "Premium Health Coverage"
    assert doc.client_name == "Acme Corp"
    assert doc.policy_id == "POL-001"


def test_repository_unknown_id():
    from repository.policy_repository import DocumentRepository
    repo = DocumentRepository()
    assert repo.get_by_id("bad_id") is None


def test_repository_date_called():
    from repository.policy_repository import DocumentRepository
    repo = DocumentRepository()
    doc = repo.get_by_id("Fake_id")
    assert doc.date_called == date.today().isoformat()


# ── Tool Registry ─────────────────────────────────────────────────────────────

def test_registry_get_tool():
    from backoffice_mcp.tool_registry import get_tool
    tool = get_tool("get_document")
    assert callable(tool)


def test_registry_missing_tool():
    from backoffice_mcp.tool_registry import get_tool
    assert get_tool("nonexistent") is None


# ── Tools ─────────────────────────────────────────────────────────────────────

def test_tool_get_document():
    from backoffice_mcp.tools import get_document
    from repository.policy_repository import PolicyDocument
    doc = get_document("Fake_id")
    assert isinstance(doc, PolicyDocument)
    assert doc.policy_name == "Premium Health Coverage"


def test_tool_unknown_id_raises():
    from backoffice_mcp.tools import get_document
    with pytest.raises(ValueError, match="not found"):
        get_document("bad_id")


# ── A2A Endpoints ─────────────────────────────────────────────────────────────

from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    from main import app
    return TestClient(app)


def test_a2a_agent_card(client):
    response = client.get("/.well-known/agent.json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Backoffice Agent"


def test_a2a_task_success(client):
    response = client.post("/tasks/send", json={
        "id": "task-1",
        "message": {"parts": [{"text": "Fake_id"}]},
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "completed"
    assert data["result"]["policy_name"] == "Premium Health Coverage"
    assert data["result"]["client_name"] == "Acme Corp"
    assert data["result"]["policy_id"] == "POL-001"
    assert "date_called" in data["result"]


def test_a2a_task_unknown_id(client):
    response = client.post("/tasks/send", json={
        "id": "task-2",
        "message": {"parts": [{"text": "bad_id"}]},
    })
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "failed"
    assert "not found" in data["error"]


def test_a2a_missing_message(client):
    response = client.post("/tasks/send", json={"id": "task-3"})
    assert response.status_code == 400
