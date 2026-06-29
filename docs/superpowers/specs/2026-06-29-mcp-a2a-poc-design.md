# MCP + A2A PoC — Design Spec

**Date:** 2026-06-29
**Status:** Approved

---

## Goal

A Python proof-of-concept server that speaks both the **A2A** (Agent-to-Agent) and **MCP** (Model Context Protocol) protocols. It exposes a single `get_document` tool that accepts a document ID and returns fake policy data. The architecture is layered so each file has one clear responsibility; the repository layer uses mocked data today and can be swapped for a real database tomorrow.

---

## Architecture

```
Another agent / the invoice system
        |  (HTTP + JSON-RPC)
        v
1. PROTOCOL LAYER    ->  main.py
   Receives the web request, validates shape. No business logic.
        |
        v
2. AGENT LAYER       ->  agent/backoffice_agent.py
   Reads the message, figures out what is being asked.
        |
        v
3. MCP SERVER        ->  mcp/mcp_server.py
   Checks the tool exists, then runs it.
        |
        v
4. TOOL REGISTRY     ->  mcp/tool_registry.py
   Maps a tool name -> the actual function.
        |
        v
5. TOOLS             ->  mcp/tools.py
   The actual logic of one tool.
        |
        v
6. REPOSITORY        ->  repository/policy_repository.py
   The data. (Mock today, real DB tomorrow.)
```

---

## File Structure

```
MCP-PoC/
├── main.py
├── agent/
│   └── backoffice_agent.py
├── mcp/
│   ├── mcp_server.py
│   ├── tool_registry.py
│   └── tools.py
├── repository/
│   └── policy_repository.py
├── docs/
│   └── superpowers/specs/
│       └── 2026-06-29-mcp-a2a-poc-design.md
└── requirements.txt
```

---

## Layer Responsibilities

### 1. `main.py` — Protocol Layer
- FastAPI app
- Mounts MCP sub-app at `/mcp` (for Claude Code / Claude Desktop to connect)
- Exposes A2A endpoints:
  - `GET /.well-known/agent.json` — agent card (capabilities discovery)
  - `POST /tasks/send` — receive an A2A task
- Validates request shape (JSON-RPC structure); rejects malformed requests with HTTP 400
- Passes valid requests to the agent layer — no business logic here

### 2. `agent/backoffice_agent.py` — Agent Layer
- Receives a parsed A2A `TaskRequest`
- Reads the message text to determine which tool to invoke and with what arguments
- For this PoC: extracts the document ID from the message and calls `mcp_server.run_tool("get_document", {"document_id": ...})`
- Returns a `TaskResponse` with status `completed` and the tool result

### 3. `mcp/mcp_server.py` — MCP Server
- Instantiates a `FastMCP` server
- Registers all tools from the tool registry
- Provides a `run_tool(name, args)` method used by the agent layer
- Mounts into FastAPI at `/mcp` via `mcp.streamable_http_app()`

### 4. `mcp/tool_registry.py` — Tool Registry
- Single `TOOL_REGISTRY: dict[str, Callable]` mapping tool name → function
- `get_tool(name: str) -> Callable | None`
- Adding a new tool means adding one entry here and one function in `tools.py`

### 5. `mcp/tools.py` — Tools
- `get_document(document_id: str) -> PolicyDocument`
- Calls `policy_repository.get_by_id(document_id)`
- Raises `ValueError` if document not found (surfaces as tool error)

### 6. `repository/policy_repository.py` — Repository
- `PolicyDocument(BaseModel)` — Pydantic model:
  - `policy_name: str`
  - `client_name: str`
  - `policy_id: str`
  - `date_called: str`  (ISO date string, set to today when record is fetched)
- `DocumentRepository` class:
  - `_store: dict[str, PolicyDocument]` seeded with `"Fake_id"`
  - `get_by_id(document_id: str) -> PolicyDocument | None`
- Module-level singleton: `policy_repository = DocumentRepository()`

---

## A2A Protocol (minimal)

**Agent card** (`/.well-known/agent.json`):
```json
{
  "name": "Backoffice Agent",
  "description": "Looks up policy documents by ID",
  "version": "0.1.0",
  "capabilities": ["get_document"]
}
```

**Task request** (`POST /tasks/send`):
```json
{
  "id": "task-123",
  "message": {
    "parts": [{ "text": "Fake_id" }]
  }
}
```

**Task response**:
```json
{
  "id": "task-123",
  "status": "completed",
  "result": {
    "policy_name": "Premium Health Coverage",
    "client_name": "Acme Corp",
    "policy_id": "POL-001",
    "date_called": "2026-06-29"
  }
}
```

Task lifecycle for this PoC: `submitted` → `completed` synchronously (no async queue).

---

## MCP Protocol

- Transport: Streamable HTTP at `/mcp`
- Tool name: `get_document`
- Input schema: `{ "document_id": "string" }`
- Output: serialized `PolicyDocument`
- Claude Code connects by adding the server URL to MCP settings

---

## Fake Data

Seeded in `DocumentRepository._store`:

| `document_id` | `policy_name`             | `client_name` | `policy_id` |
|---------------|---------------------------|---------------|-------------|
| `Fake_id`     | Premium Health Coverage   | Acme Corp     | POL-001     |

`date_called` is set dynamically to today's date at fetch time.

---

## Dependencies (`requirements.txt`)

```
fastapi
uvicorn
mcp[cli]
pydantic
```

---

## Error Handling

- Unknown document ID → `ValueError` in `tools.py` → A2A response with `status: failed`, MCP surfaces as tool error
- Missing `document_id` in A2A message → HTTP 400 from protocol layer
- Unknown tool name → `KeyError` in registry → HTTP 400

---

## Success Criteria

1. `uvicorn main:app` starts without errors
2. `GET /.well-known/agent.json` returns the agent card
3. `POST /tasks/send` with `"Fake_id"` returns full policy data
4. `POST /tasks/send` with an unknown ID returns `status: failed`
5. Claude Code can connect to `/mcp` and invoke `get_document` directly
