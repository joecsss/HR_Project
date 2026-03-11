"""Audit logging service for transparency and tracing."""

from sqlalchemy.orm import Session
from app.models.audit import AuditLog
from typing import Optional


def create_audit_log(
    db: Session,
    action: str,
    user_id: Optional[int] = None,
    entity_type: Optional[str] = None,
    entity_id: Optional[int] = None,
    details: Optional[str] = None,
    prompt_text: Optional[str] = None,
    response_text: Optional[str] = None,
    metadata_json: Optional[dict] = None,
    ip_address: Optional[str] = None,
) -> AuditLog:
    """Create an audit log entry."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=entity_id,
        details=details,
        prompt_text=prompt_text,
        response_text=response_text,
        metadata_json=metadata_json,
        ip_address=ip_address,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def get_audit_logs(
    db: Session,
    skip: int = 0,
    limit: int = 50,
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
):
    """Retrieve audit logs with optional filtering."""
    query = db.query(AuditLog)
    if action:
        query = query.filter(AuditLog.action == action)
    if entity_type:
        query = query.filter(AuditLog.entity_type == entity_type)
    total = query.count()
    logs = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()
    return logs, total
