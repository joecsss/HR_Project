"""Chatbot API routes for HR Assistant."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.orm import Session
import uuid

from app.database import get_db
from app.models.user import User
from app.api.auth import get_current_user
from app.services.chatbot import chat, clear_session
from app.services.audit import create_audit_log

router = APIRouter(prefix="/api/chatbot", tags=["Chatbot"])


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    context: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


@router.post("", response_model=ChatResponse)
async def send_message(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Send a message to the HR chatbot."""
    session_id = request.session_id or str(uuid.uuid4())

    reply = chat(
        message=request.message,
        session_id=session_id,
        context=request.context,
    )

    create_audit_log(
        db, action="chatbot_message", user_id=current_user.id,
        entity_type="chatbot",
        details=f"Chat session: {session_id}",
        prompt_text=request.message[:500],
        response_text=reply[:500],
    )

    return ChatResponse(reply=reply, session_id=session_id)


@router.delete("/session/{session_id}")
async def end_session(
    session_id: str,
    current_user: User = Depends(get_current_user),
):
    """Clear conversation history for a chat session."""
    clear_session(session_id)
    return {"message": "Session cleared"}
