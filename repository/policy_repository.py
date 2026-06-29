from datetime import date
from pydantic import BaseModel


class PolicyDocument(BaseModel):
    policy_name: str
    client_name: str
    policy_id: str
    date_called: str


class DocumentRepository:
    def __init__(self):
        self._store: dict[str, dict] = {
            "Fake_id": {
                "policy_name": "Premium Health Coverage",
                "client_name": "Acme Corp",
                "policy_id": "POL-001",
            }
        }

    def get_by_id(self, document_id: str) -> PolicyDocument | None:
        record = self._store.get(document_id)
        if record is None:
            return None
        return PolicyDocument(**record, date_called=date.today().isoformat())


policy_repository = DocumentRepository()
