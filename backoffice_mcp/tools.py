from repository.policy_repository import PolicyDocument, policy_repository


def get_document(document_id: str) -> PolicyDocument:
    doc = policy_repository.get_by_id(document_id)
    if doc is None:
        raise ValueError(f"Document '{document_id}' not found")
    return doc
