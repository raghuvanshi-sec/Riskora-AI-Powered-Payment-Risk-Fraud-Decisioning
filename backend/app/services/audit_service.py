"""Lightweight audit logging service.

Writes AuditLog rows within the caller's DB session so audit events are
committed together with the originating transaction. No separate connection
or retry logic is needed for this phase.
"""

from typing import Any, Optional
from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def log_audit(
    db: Session,
    *,
    action: str,
    entity_type: str,
    entity_id: Optional[str] = None,
    user_id: Optional[int] = None,
    details: Optional[Any] = None,
) -> AuditLog:
    """Insert an audit log row and return it (not flushed to DB by caller)."""
    details_str: Optional[str] = None
    if details is not None and not isinstance(details, str):
        import json

        details_str = json.dumps(details, default=str)
    elif isinstance(details, str):
        details_str = details

    audit = AuditLog(
        user_id=user_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id) if entity_id is not None else None,
        details=details_str,
    )
    db.add(audit)
    return audit