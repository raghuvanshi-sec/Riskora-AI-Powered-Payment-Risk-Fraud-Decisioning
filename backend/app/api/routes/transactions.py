"""Transaction REST endpoints.

Thin handlers — all logic lives in transaction_service. Authz:
- any authenticated active user may read
- RISK_ANALYST / ADMIN may create and patch

Paths are absolute here; the router is included without a prefix
in `app/api/routes/__init__.py` to avoid `/transactions/transactions`.
"""

from typing import Optional

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user, require_risk_analyst
from app.db.database import get_db
from app.models.user import User
from app.schemas.transaction import (
    PaginatedResponse,
    TransactionCreate,
    TransactionDetail,
    TransactionListItem,
    TransactionResponse,
    TransactionSummary,
    TransactionUpdate,
)
from app.services import transaction_service
from app.services.audit_service import log_audit

router = APIRouter()


@router.post(
    "/transactions",
    response_model=TransactionResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["transactions"],
)
def create_transaction(
    *,
    db: Session = Depends(get_db),
    tx_in: TransactionCreate,
    current_user: User = Depends(require_risk_analyst),
):
    try:
        tx = transaction_service.create_transaction(
            db,
            transaction_reference=tx_in.transaction_reference,
            user_id=tx_in.user_id,
            merchant_id=tx_in.merchant_id,
            amount=tx_in.amount,
            currency=tx_in.currency,
            device_id=tx_in.device_id,
            location=tx_in.location,
            transaction_timestamp=tx_in.transaction_timestamp,
            account_age_days=tx_in.account_age_days,
            previous_transaction_amount=tx_in.previous_transaction_amount,
            transaction_frequency=tx_in.transaction_frequency,
            failed_attempts=tx_in.failed_attempts,
            device_change=tx_in.device_change,
            location_change=tx_in.location_change,
            merchant_risk=tx_in.merchant_risk,
            velocity=tx_in.velocity,
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except (IntegrityError, ValidationError) as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Constraint violation: {e}",
        )

    log_audit(
        db,
        action="CREATED",
        entity_type="TRANSACTION",
        entity_id=tx.id,
        user_id=current_user.id,
        details={"transaction_reference": tx.transaction_reference},
    )
    db.commit()
    return tx


@router.get(
    "/transactions",
    response_model=PaginatedResponse[TransactionListItem],
    tags=["transactions"],
)
def list_transactions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = Query("transaction_timestamp"),
    sort_order: str = Query("desc"),
    search: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    merchant_id: Optional[int] = Query(None),
    risk_level: Optional[str] = Query(None),
    decision: Optional[str] = Query(None),
):
    try:
        items, total = transaction_service.list_transactions(
            db,
            page=page,
            page_size=page_size,
            sort_by=sort_by,
            sort_order=sort_order,
            search=search,
            user_id=user_id,
            merchant_id=merchant_id,
            risk_level=risk_level,
            decision=decision,
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    return PaginatedResponse(
        items=items,
        page=page,
        page_size=page_size,
        total=total,
        total_pages=total_pages,
    )


@router.get(
    "/transactions/summary",
    response_model=TransactionSummary,
    tags=["transactions"],
)
def get_transactions_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return transaction_service.get_summary(db)


@router.get(
    "/transactions/recent",
    response_model=list[TransactionListItem],
    tags=["transactions"],
)
def get_recent_transactions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(5, ge=1, le=20),
):
    return transaction_service.get_recent_transactions(db, limit=limit)


@router.get(
    "/transactions/{transaction_id}",
    response_model=TransactionDetail,
    tags=["transactions"],
)
def get_transaction(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    tx = transaction_service.get_transaction(db, transaction_id)
    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return tx


@router.patch(
    "/transactions/{transaction_id}",
    response_model=TransactionResponse,
    tags=["transactions"],
)
def patch_transaction(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    tx_in: TransactionUpdate,
    current_user: User = Depends(require_risk_analyst),
):
    updates = tx_in.model_dump(exclude_none=True)
    try:
        tx = transaction_service.patch_transaction(db, transaction_id, **updates)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )

    if not tx:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    log_audit(
        db,
        action="UPDATED",
        entity_type="TRANSACTION",
        entity_id=tx.id,
        user_id=current_user.id,
        details={"patched_fields": sorted(updates.keys())},
    )
    db.commit()
    return tx