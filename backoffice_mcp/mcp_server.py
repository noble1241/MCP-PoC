from mcp.server.fastmcp import FastMCP
from backoffice_mcp.tool_registry import get_tool

mcp_app = FastMCP("Backoffice Agent")


@mcp_app.tool()
def get_document(document_id: str) -> dict:
    """Look up a policy document by its ID."""
    return get_tool("get_document")(document_id).model_dump()


def run_tool(name: str, args: dict):
    tool_fn = get_tool(name)
    if tool_fn is None:
        raise KeyError(f"Tool '{name}' not found in registry")
    return tool_fn(**args)
