"""Risk operations service — analyst workflow, cases, and actions."""

from datetime import datetime, timezone
from typing import Optional, List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from app.models.risk_ops import RiskCase, AnalystAction, CaseStatus, CasePriority, ActionType
from app.models.transaction import Transaction
from app.models.risk import RiskAssessment
from app.services.audit_service import log_audit


def create_case(
    db: Session,
    transaction_id: int,
    risk_score: int,
    risk_level: str,
    decision: str,
    priority: str = CasePriority.MEDIUM.value,
    summary: Optional[str] = None,
    user_id: Optional[int] = None,
) -> RiskCase:
    case = RiskCase(
        transaction_id=transaction_id,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        priority=priority,
        summary=summary,
        status=CaseStatus.OPEN.value,
    )
    db.add(case)
    db.flush()

    log_audit(
        db,
        action=f"CASE_CREATED: transaction={transaction_id} decision={decision}",
        entity_type="RISK_CASE",
        entity_id=str(case.id),
        user_id=user_id,
        details={"transaction_id": transaction_id, "risk_score": risk_score, "risk_level": risk_level, "decision": decision},
    )

    return case


def get_case_by_id(db: Session, case_id: int) -> Optional[RiskCase]:
    return db.query(RiskCase).filter(RiskCase.id == case_id).first()


def get_case_by_transaction(db: Session, transaction_id: int) -> Optional[RiskCase]:
    return (
        db.query(RiskCase)
        .filter(RiskCase.transaction_id == transaction_id)
        .order_by(desc(RiskCase.created_at))
        .first()
    )


def list_cases(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    assigned_analyst_id: Optional[int] = None,
    risk_level: Optional[str] = None,
) -> Tuple[List[RiskCase], int]:
    q = db.query(RiskCase)

    if status:
        q = q.filter(RiskCase.status == status)
    if priority:
        q = q.filter(RiskCase.priority == priority)
    if assigned_analyst_id:
        q = q.filter(RiskCase.assigned_analyst_id == assigned_analyst_id)
    if risk_level:
        q = q.filter(RiskCase.risk_level == risk_level)

    total = q.count()
    cases = (
        q.order_by(desc(RiskCase.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return cases, total


def get_review_queue(
    db: Session,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[RiskCase], int]:
    """Return cases that need analyst attention: OPEN or IN_PROGRESS."""
    q = db.query(RiskCase).filter(
        RiskCase.status.in_([CaseStatus.OPEN.value, CaseStatus.IN_PROGRESS.value])
    )
    total = q.count()
    cases = (
        q.order_by(desc(RiskCase.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return cases, total


def assign_case(
    db: Session,
    case_id: int,
    analyst_id: int,
    user_id: Optional[int] = None,
) -> Optional[RiskCase]:
    case = get_case_by_id(db, case_id)
    if not case:
        return None

    old_status = case.status
    case.assigned_analyst_id = analyst_id
    if case.status == CaseStatus.OPEN.value:
        case.status = CaseStatus.IN_PROGRESS.value
    db.flush()

    log_audit(
        db,
        action=f"CASE_ASSIGNED: analyst={analyst_id}",
        entity_type="RISK_CASE",
        entity_id=str(case_id),
        user_id=user_id,
        details={"case_id": case_id, "analyst_id": analyst_id, "previous_status": old_status},
    )

    return case


def update_case(
    db: Session,
    case_id: int,
    user_id: Optional[int] = None,
    status: Optional[str] = None,
    priority: Optional[str] = None,
    summary: Optional[str] = None,
    internal_notes: Optional[str] = None,
) -> Optional[RiskCase]:
    case = get_case_by_id(db, case_id)
    if not case:
        return None

    if status is not None:
        case.status = status
        if status == CaseStatus.RESOLVED.value:
            case.resolved_at = datetime.now(timezone.utc)

    if priority is not None:
        case.priority = priority
    if summary is not None:
        case.summary = summary
    if internal_notes is not None:
        case.internal_notes = internal_notes

    db.flush()

    log_audit(
        db,
        action=f"CASE_UPDATED",
        entity_type="RISK_CASE",
        entity_id=str(case_id),
        user_id=user_id,
        details={"case_id": case_id, "status": status, "priority": priority},
    )

    return case


def record_action(
    db: Session,
    case_id: int,
    action_type: str,
    analyst_id: Optional[int] = None,
    user_id: Optional[int] = None,
    reason: Optional[str] = None,
    previous_status: Optional[str] = None,
    new_status: Optional[str] = None,
    metadata: Optional[str] = None,
) -> AnalystAction:
    action = AnalystAction(
        risk_case_id=case_id,
        analyst_id=analyst_id,
        action_type=action_type,
        reason=reason,
        previous_status=previous_status,
        new_status=new_status,
        metadata=metadata,
    )
    db.add(action)
    db.flush()

    log_audit(
        db,
        action=f"ANALYST_ACTION: {action_type}",
        entity_type="RISK_CASE",
        entity_id=str(case_id),
        user_id=user_id,
        details={
            "case_id": case_id,
            "action_type": action_type,
            "reason": reason,
            "previous_status": previous_status,
            "new_status": new_status,
        },
    )

    return action


def get_case_actions(
    db: Session,
    case_id: int,
    page: int = 1,
    page_size: int = 50,
) -> Tuple[List[AnalystAction], int]:
    q = db.query(AnalystAction).filter(AnalystAction.risk_case_id == case_id)
    total = q.count()
    actions = (
        q.order_by(desc(AnalystAction.created_at))
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return actions, total


def get_case_with_transaction(db: Session, case_id: int) -> Optional[dict]:
    case = (
        db.query(RiskCase)
        .filter(RiskCase.id == case_id)
        .first()
    )
    if not case:
        return None

    tx = (
        db.query(Transaction)
        .filter(Transaction.id == case.transaction_id)
        .first()
    )

    assessment = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.transaction_id == case.transaction_id)
        .order_by(desc(RiskAssessment.created_at))
        .first()
    )

    actions = (
        db.query(AnalystAction)
        .filter(AnalystAction.risk_case_id == case_id)
        .order_by(desc(AnalystAction.created_at))
        .limit(20)
        .all()
    )

    result = {
        "id": case.id,
        "transaction_id": case.transaction_id,
        "assigned_analyst_id": case.assigned_analyst_id,
        "status": case.status,
        "priority": case.priority,
        "risk_score": case.risk_score,
        "risk_level": case.risk_level,
        "decision": case.decision,
        "summary": case.summary,
        "internal_notes": case.internal_notes,
        "created_at": case.created_at,
        "updated_at": case.updated_at,
        "resolved_at": case.resolved_at,
        "transaction": None,
        "risk_assessment": None,
        "analyst_actions": [],
    }

    if tx:
        result["transaction"] = {
            "id": tx.id,
            "transaction_reference": tx.transaction_reference,
            "amount": tx.amount,
            "currency": tx.currency,
            "device_id": tx.device_id,
            "location": tx.location,
            "transaction_timestamp": tx.transaction_timestamp,
            "user_id": tx.user_id,
            "merchant_id": tx.merchant_id,
            "risk_score": tx.risk_score,
            "risk_level": tx.risk_level,
            "decision": tx.decision,
        }

    if assessment:
        result["risk_assessment"] = {
            "id": assessment.id,
            "risk_score": assessment.risk_score,
            "risk_level": assessment.risk_level,
            "decision": assessment.decision,
            "explanation": assessment.explanation,
            "model_version": assessment.model_version,
            "created_at": assessment.created_at,
        }

    if actions:
        result["analyst_actions"] = [
            {
                "id": a.id,
                "action_type": a.action_type,
                "reason": a.reason,
                "previous_status": a.previous_status,
                "new_status": a.new_status,
                "metadata": a.metadata,
                "created_at": a.created_at,
                "analyst_id": a.analyst_id,
            }
            for a in actions
        ]

    return result


def get_queue_stats(db: Session) -> dict:
    total = db.query(func.count(RiskCase.id)).scalar() or 0
    open_count = (
        db.query(func.count(RiskCase.id))
        .filter(RiskCase.status == CaseStatus.OPEN.value)
        .scalar()
        or 0
    )
    in_progress = (
        db.query(func.count(RiskCase.id))
        .filter(RiskCase.status == CaseStatus.IN_PROGRESS.value)
        .scalar()
        or 0
    )
    escalated = (
        db.query(func.count(RiskCase.id))
        .filter(RiskCase.status == CaseStatus.ESCALATED.value)
        .scalar()
        or 0
    )
    resolved = (
        db.query(func.count(RiskCase.id))
        .filter(RiskCase.status == CaseStatus.RESOLVED.value)
        .scalar()
        or 0
    )
    critical = (
        db.query(func.count(RiskCase.id))
        .filter(RiskCase.priority == CasePriority.CRITICAL.value)
        .filter(RiskCase.status.in_([CaseStatus.OPEN.value, CaseStatus.IN_PROGRESS.value]))
        .scalar()
        or 0
    )
    return {
        "total": total,
        "open": open_count,
        "in_progress": in_progress,
        "escalated": escalated,
        "resolved": resolved,
        "critical": critical,
    }
