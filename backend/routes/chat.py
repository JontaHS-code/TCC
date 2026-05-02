from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/chat", tags=["Chat"])

class ChatMessage(BaseModel):
    message: str

@router.post("/")
def chat_endpoint(msg: ChatMessage):
    # Placeholder para futura integração com LLM via RAG
    return {"response": f"Simulei uma resposta para: {msg.message}. Em breve, integraremos IA generativa!"}