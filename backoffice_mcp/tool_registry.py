from typing import Callable
from backoffice_mcp.tools import get_document

TOOL_REGISTRY: dict[str, Callable] = {
    "get_document": get_document,
}


def get_tool(name: str) -> Callable | None:
    return TOOL_REGISTRY.get(name)
