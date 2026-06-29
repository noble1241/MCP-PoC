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
