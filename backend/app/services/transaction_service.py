"""Transaction service layer.

All DB/business logic for transactions lives here. Risk scoring is
explicitly out of scope — `risk_score`/`risk_level`/`decision` are never
computed or written by this service; they stay NULL until a later phase.
"""

from datetime import datetime, date
from typing import Optional

from sqlalchemy import or_, asc, desc, func
from sqlalchemy.orm import Session, selectinload

from app.models.transaction import Transaction
from app.models.user import User
from app.models.merchant import Merchant

# Columns allowed as sort keys. Everything else is rejected to avoid
# arbitrary SQL injection through the `sort_by` query parameter.
ALLOWED_SORT_FIELDS = {
    "id": Transaction.id,
    "transaction_reference": Transaction.transaction_reference,
    "amount": Transaction.amount,
    "currency": Transaction.currency,
    "transaction_timestamp": Transaction.transaction_timestamp,
    "created_at": Transaction.created_at,
    "device_id": Transaction.device_id,
    "location": Transaction.location,
    "account_age_days": Transaction.account_age_days,
    "failed_attempts": Transaction.failed_attempts,
    "velocity": Transaction.velocity,
    "merchant_risk": Transaction.merchant_risk,
}


def _validate_foreign_keys(db: Session, user_id: int, merchant_id: int) -> None:
    """Ensure referenced user/merchant exist. Raises ValueError if not."""
    if not db.query(User).filter(User.id == user_id).first():
        raise ValueError(f"User with id={user_id} does not exist")
    if not db.query(Merchant).filter(Merchant.id == merchant_id).first():
        raise ValueError(f"Merchant with id={merchant_id} does not exist")


def create_transaction(
    db: Session,
    *,
    transaction_reference: str,
    user_id: int,
    merchant_id: int,
    amount: float,
    currency: str = "INR",
    device_id: Optional[str] = None,
    location: Optional[str] = None,
    transaction_timestamp: datetime,
    account_age_days: Optional[int] = None,
    previous_transaction_amount: Optional[float] = None,
    transaction_frequency: Optional[int] = None,
    failed_attempts: Optional[int] = None,
    device_change: Optional[bool] = False,
    location_change: Optional[bool] = False,
    merchant_risk: Optional[float] = None,
    velocity: Optional[int] = None,
) -> Transaction:
    """Create a new transaction. Risk fields are intentionally left unset.

    Raises ValueError if the transaction_reference already exists or if
    the user_id/merchant_id FKs are invalid.
    """
    _validate_foreign_keys(db, user_id, merchant_id)

    existing = (
        db.query(Transaction)
        .filter(Transaction.transaction_reference == transaction_reference)
        .first()
    )
    if existing:
        raise ValueError(
            f"Transaction with reference '{transaction_reference}' already exists"
        )

    tx = Transaction(
        transaction_reference=transaction_reference,
        user_id=user_id,
        merchant_id=merchant_id,
        amount=amount,
        currency=currency,
        device_id=device_id,
        location=location,
        transaction_timestamp=transaction_timestamp,
        account_age_days=account_age_days,
        previous_transaction_amount=previous_transaction_amount,
        transaction_frequency=transaction_frequency,
        failed_attempts=failed_attempts,
        device_change=device_change,
        location_change=location_change,
        merchant_risk=merchant_risk,
        velocity=velocity,
        # risk_score / risk_level / decision intentionally NULL — no scoring here
    )
    db.add(tx)
    db.commit()
    db.refresh(tx)
    return tx


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Fetch a single transaction by PK, eager-loading user/merchant."""
    return (
        db.query(Transaction)
        .options(selectinload(Transaction.user), selectinload(Transaction.merchant))
        .filter(Transaction.id == transaction_id)
        .first()
    )

def get_transaction_by_reference(
    db: Session, transaction_reference: str
) -> Optional[Transaction]:
    """Fetch a single transaction by reference, eager-loading user/merchant."""
    return (
        db.query(Transaction)
        .options(selectinload(Transaction.user), selectinload(Transaction.merchant))
        .filter(Transaction.transaction_reference == transaction_reference)
        .first()
    )


def list_transactions(
    db: Session,
    *,
    page: int = 1,
    page_size: int = 20,
    sort_by: str = "transaction_timestamp",
    sort_order: str = "desc",
    search: Optional[str] = None,
    user_id: Optional[int] = None,
    merchant_id: Optional[int] = None,
    risk_level: Optional[str] = None,
    decision: Optional[str] = None,
) -> tuple[list[Transaction], int]:
    """List transactions with DB-level pagination, filtering, and sorting.

    Returns (items, total_count). `search` matches against user name, merchant
    name, transaction reference, and location. `sort_by` is allowlisted.
    """
    max_page_size = 100
    if page_size > max_page_size:
        page_size = max_page_size
    if page < 1:
        page = 1

    sort_col = ALLOWED_SORT_FIELDS.get(sort_by)
    if sort_col is None:
        raise ValueError(f"Invalid sort field: {sort_by}")

    q = db.query(Transaction).options(
        selectinload(Transaction.user), selectinload(Transaction.merchant)
    )

    if user_id is not None:
        q = q.filter(Transaction.user_id == user_id)
    if merchant_id is not None:
        q = q.filter(Transaction.merchant_id == merchant_id)
    if risk_level is not None:
        # risk_level lives on the transaction itself (Optional[str])
        q = q.filter(Transaction.risk_level == risk_level)
    if decision is not None:
        q = q.filter(Transaction.decision == decision)

    if search:
        pattern = f"%{search}%"
        q = q.join(User, Transaction.user_id == User.id, isouter=True).join(
            Merchant, Transaction.merchant_id == Merchant.id, isouter=True
        ).filter(
            or_(
                Transaction.transaction_reference.ilike(pattern),
                Transaction.location.ilike(pattern),
                User.name.ilike(pattern),
                Merchant.name.ilike(pattern),
            )
        )

    order_col = asc(sort_col) if sort_order == "asc" else desc(sort_col)
    total = q.order_by(None).count()
    items = q.order_by(order_col).offset((page - 1) * page_size).limit(page_size).all()
    return items, total


def patch_transaction(
    db: Session, transaction_id: int, **updates
) -> Optional[Transaction]:
    """Apply partial updates to a transaction. Only allowlisted fields are
    accepted; unknown keys raise ValueError.

    `transaction_reference`, `created_at`, `amount`, and
    `transaction_timestamp` are immutable and cannot be patched.
    """
    allowed = {
        "device_id",
        "location",
        "account_age_days",
        "previous_transaction_amount",
        "transaction_frequency",
        "failed_attempts",
        "device_change",
        "location_change",
        "merchant_risk",
        "velocity",
    }
    unknown = set(updates.keys()) - allowed
    if unknown:
        raise ValueError(f"Cannot patch immutable fields: {sorted(unknown)}")

    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return None

    for key, value in updates.items():
        if value is None and key in ("device_change", "location_change"):
            # Allow explicit null reset for booleans
            setattr(tx, key, None)
            continue
        setattr(tx, key, value)

    db.commit()
    db.refresh(tx)
    return tx


def get_recent_transactions(db: Session, limit: int = 5) -> list[Transaction]:
    """Return the most recent transactions sorted by transaction_timestamp desc."""
    max_limit = 20
    if limit > max_limit:
        limit = max_limit
    if limit < 1:
        limit = 1

    return (
        db.query(Transaction)
        .options(selectinload(Transaction.user), selectinload(Transaction.merchant))
        .order_by(desc(Transaction.transaction_timestamp))
        .limit(limit)
        .all()
    )


def get_summary(db: Session) -> dict:
    """Return aggregate counts/sums for the dashboard."""
    today = datetime.combine(date.today(), datetime.min.time())

    total_transactions = db.query(Transaction).count()
    total_amount = float(
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0)).scalar() or 0.0
    )
    today_count = (
        db.query(Transaction)
        .filter(Transaction.transaction_timestamp >= today)
        .count()
    )
    today_amount = float(
        db.query(func.coalesce(func.sum(Transaction.amount), 0.0))
        .filter(Transaction.transaction_timestamp >= today)
        .scalar()
        or 0.0
    )

    return {
        "total_transactions": total_transactions,
        "total_amount": total_amount,
        "today_transactions": today_count,
        "today_amount": today_amount,
    }