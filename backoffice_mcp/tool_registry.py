from typing import Callable

TOOL_REGISTRY: dict[str, Callable] = {}


def get_tool(name: str) -> Callable | None:
    return TOOL_REGISTRY.get(name)
