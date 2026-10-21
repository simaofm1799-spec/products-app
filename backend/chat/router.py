from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from chat.service import chat_service
from common.schemas import ERROR_RESPONSES
from common.security import get_current_user


class HistoryEntry(BaseModel):
    role: str
    text: str


class ChatRequest(BaseModel):
    question: str = Field(max_length=500, min_length=1)
    history: list[HistoryEntry] = Field(default_factory=list)


class ChatResponse(BaseModel):
    answer: str


router = APIRouter(
    prefix="/api/chat",
    responses=ERROR_RESPONSES,
    tags=["chat"],
)


@router.post("", response_model=ChatResponse, summary="Ask a natural-language question about the data")
async def ask(body: ChatRequest, _user: dict = Depends(get_current_user)) -> dict:
    answer = await chat_service.answer(body.question, [h.model_dump() for h in body.history])
    return {"answer": answer}
