"""Pydantic schemas for Audit Log operations."""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime


class AuditLogResponse(BaseModel):
    id: int
    user_id: Optional[int] = None
    action: str
    entity_type: Optional[str] = None
    entity_id: Optional[int] = None
    details: Optional[str] = None
    prompt_text: Optional[str] = None
    response_text: Optional[str] = None
    metadata_json: Optional[dict] = None
    created_at: datetime

    model_config = {"from_attributes": True}


class AuditLogListResponse(BaseModel):
    logs: List[AuditLogResponse]
    total: int
