from typing import Any
from pydantic import BaseModel
from backoffice_mcp.mcp_server import run_tool


class MessagePart(BaseModel):
    text: str


class Message(BaseModel):
    parts: list[MessagePart]


class TaskRequest(BaseModel):
    id: str
    message: Message


class TaskResponse(BaseModel):
    id: str
    status: str
    result: Any = None
    error: str | None = None


class BackofficeAgent:
    def handle(self, request: TaskRequest) -> TaskResponse:
        document_id = request.message.parts[0].text.strip()
        try:
            result = run_tool("get_document", {"document_id": document_id})
            return TaskResponse(
                id=request.id,
                status="completed",
                result=result.model_dump(),
            )
        except (ValueError, KeyError) as e:
            return TaskResponse(
                id=request.id,
                status="failed",
                error=str(e),
            )


backoffice_agent = BackofficeAgent()
