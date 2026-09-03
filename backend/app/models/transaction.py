from sqlalchemy import String, DateTime, Integer, Float, ForeignKey, CheckConstraint, func, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List, Optional
from app.db.database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_reference: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), index=True, nullable=False)
    merchant_id: Mapped[int] = mapped_column(Integer, ForeignKey("merchants.id", ondelete="CASCADE"), index=True, nullable=False)
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), nullable=False, default="INR")
    device_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    location: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    transaction_timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    account_age_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    previous_transaction_amount: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    transaction_frequency: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    failed_attempts: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    device_change: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    location_change: Mapped[Optional[bool]] = mapped_column(Boolean, default=False, nullable=True)
    merchant_risk: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    velocity: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    # Constraints
    __table_args__ = (
        CheckConstraint("amount >= 0", name="check_transaction_amount_non_negative"),
    )

    # Relationships
    user: Mapped["User"] = relationship("User", back_populates="transactions")
    merchant: Mapped["Merchant"] = relationship("Merchant", back_populates="transactions")
    risk_assessments: Mapped[List["RiskAssessment"]] = relationship(
        "RiskAssessment", 
        back_populates="transaction", 
        cascade="all, delete-orphan"
    )
    risk_events: Mapped[List["RiskEvent"]] = relationship(
        "RiskEvent", 
        back_populates="transaction", 
        cascade="all, delete-orphan"
    )
    risk_cases: Mapped[List["RiskCase"]] = relationship(
        "RiskCase", 
        back_populates="transaction", 
        cascade="all, delete-orphan"
    )
