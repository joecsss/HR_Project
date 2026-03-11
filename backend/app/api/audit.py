"""Audit log API routes for transparency."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.schemas.audit import AuditLogListResponse
from app.api.auth import require_admin
from app.services.audit import get_audit_logs

router = APIRouter(prefix="/api/audit", tags=["Audit"])


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    """List audit logs (admin only)."""
    logs, total = get_audit_logs(
        db, skip=skip, limit=limit,
        action=action, entity_type=entity_type,
    )
    return AuditLogListResponse(logs=logs, total=total)
