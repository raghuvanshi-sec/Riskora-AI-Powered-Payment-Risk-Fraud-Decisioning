"""Risk Operations API — analyst workflow, cases, and audit actions."""

import math
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_risk_analyst
from app.db.database import get_db
from app.models.user import User
from app.models.risk_ops import CaseStatus, ActionType
from app.schemas.risk_ops import (
    CaseCreate,
    CaseUpdate,
    CaseAssign,
    CaseResponse,
    CaseListResponse,
    CaseDetailResponse,
    AnalystActionCreate,
    AnalystActionResponse,
    PaginatedCasesResponse,
    PaginatedActionsResponse,
)
from app.services import risk_ops_service

router = APIRouter()


@router.post(
    "/cases",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["risk-ops"],
)
def create_case(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
    case_in: CaseCreate,
):
    from app.services import transaction_service
    tx = transaction_service.get_transaction_by_id(db, case_in.transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    existing = risk_ops_service.get_case_by_transaction(db, case_in.transaction_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"A case already exists for transaction {case_in.transaction_id}",
        )

    risk_score = tx.risk_score or 0
    risk_level = tx.risk_level or "MEDIUM"
    decision = tx.decision or "REVIEW"

    case = risk_ops_service.create_case(
        db,
        transaction_id=case_in.transaction_id,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        priority=case_in.priority,
        summary=case_in.summary,
        user_id=current_user.id,
    )
    db.commit()
    return case


@router.get(
    "/cases",
    response_model=PaginatedCasesResponse,
    tags=["risk-ops"],
)
def list_cases(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    status: str = Query(None),
    priority: str = Query(None),
    risk_level: str = Query(None),
):
    cases, total = risk_ops_service.list_cases(
        db,
        page=page,
        page_size=page_size,
        status=status,
        priority=priority,
        risk_level=risk_level,
    )
    return PaginatedCasesResponse(
        items=[CaseListResponse.model_validate(c) for c in cases],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 1,
    )


@router.get(
    "/cases/queue",
    response_model=PaginatedCasesResponse,
    tags=["risk-ops"],
)
def get_review_queue(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    cases, total = risk_ops_service.get_review_queue(
        db,
        page=page,
        page_size=page_size,
    )
    return PaginatedCasesResponse(
        items=[CaseListResponse.model_validate(c) for c in cases],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 1,
    )


@router.get(
    "/cases/stats",
    response_model=dict,
    tags=["risk-ops"],
)
def get_queue_stats(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return risk_ops_service.get_queue_stats(db)


@router.get(
    "/cases/{case_id}",
    response_model=CaseDetailResponse,
    tags=["risk-ops"],
)
def get_case(
    case_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    case_data = risk_ops_service.get_case_with_transaction(db, case_id)
    if not case_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    return case_data


@router.patch(
    "/cases/{case_id}",
    response_model=CaseResponse,
    tags=["risk-ops"],
)
def update_case(
    case_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
    case_in: CaseUpdate,
):
    case = risk_ops_service.update_case(
        db,
        case_id=case_id,
        user_id=current_user.id,
        status=case_in.status,
        priority=case_in.priority,
        summary=case_in.summary,
        internal_notes=case_in.internal_notes,
    )
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    db.commit()
    return case


@router.post(
    "/cases/{case_id}/assign",
    response_model=CaseResponse,
    tags=["risk-ops"],
)
def assign_case(
    case_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
    assign_in: CaseAssign,
):
    case = risk_ops_service.assign_case(
        db,
        case_id=case_id,
        analyst_id=assign_in.assigned_analyst_id,
        user_id=current_user.id,
    )
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )
    db.commit()
    return case


@router.post(
    "/cases/{case_id}/actions",
    response_model=AnalystActionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["risk-ops"],
)
def take_action(
    case_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
    action_in: AnalystActionCreate,
):
    case = risk_ops_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    valid_actions = [a.value for a in ActionType]
    if action_in.action_type not in valid_actions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid action type. Must be one of: {valid_actions}",
        )

    previous_status = case.status
    new_status = action_in.new_status if action_in.new_status else None

    action = risk_ops_service.record_action(
        db,
        case_id=case_id,
        action_type=action_in.action_type,
        analyst_id=current_user.id,
        user_id=current_user.id,
        reason=action_in.reason,
        previous_status=previous_status,
        new_status=new_status,
        metadata=action_in.metadata,
    )

    if new_status:
        case.status = new_status
        if new_status == CaseStatus.RESOLVED.value:
            from datetime import datetime, timezone
            case.resolved_at = datetime.now(timezone.utc)

    db.commit()
    return action


@router.get(
    "/cases/{case_id}/actions",
    response_model=PaginatedActionsResponse,
    tags=["risk-ops"],
)
def get_case_actions(
    case_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    case = risk_ops_service.get_case_by_id(db, case_id)
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found",
        )

    actions, total = risk_ops_service.get_case_actions(
        db,
        case_id=case_id,
        page=page,
        page_size=page_size,
    )
    return PaginatedActionsResponse(
        items=[AnalystActionResponse.model_validate(a) for a in actions],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 1,
    )
