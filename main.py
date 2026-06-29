from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from agent.backoffice_agent import TaskRequest, backoffice_agent
from backoffice_mcp.mcp_server import mcp_app

app = FastAPI()
app.mount("/mcp", mcp_app.streamable_http_app())

AGENT_CARD = {
    "name": "Backoffice Agent",
    "description": "Looks up policy documents by ID",
    "version": "0.1.0",
    "capabilities": ["get_document"],
}


@app.get("/.well-known/agent.json")
async def agent_card():
    return JSONResponse(AGENT_CARD)


@app.post("/tasks/send")
async def tasks_send(request: Request):
    try:
        body = await request.json()
        task_request = TaskRequest(**body)
    except Exception:
        return JSONResponse({"error": "Invalid request"}, status_code=400)
    response = backoffice_agent.handle(task_request)
    return JSONResponse(response.model_dump())
