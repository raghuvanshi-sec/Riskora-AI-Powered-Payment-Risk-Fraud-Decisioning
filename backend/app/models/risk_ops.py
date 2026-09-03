from sqlalchemy import String, DateTime, Integer, ForeignKey, Text, func, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from enum import Enum
from app.db.database import Base


class CaseStatus(str, Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    RESOLVED = "RESOLVED"
    ESCALATED = "ESCALATED"
    CLOSED = "CLOSED"


class CasePriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ActionType(str, Enum):
    ALLOW = "ALLOW"
    BLOCK = "BLOCK"
    ESCALATE = "ESCALATE"
    FLAG = "FLAG"
    WHITELIST = "WHITELIST"
    BLACKLIST = "BLACKLIST"
    ADD_NOTE = "ADD_NOTE"
    REQUEST_MORE_INFO = "REQUEST_MORE_INFO"
    DISMISS = "DISMISS"


class RiskCase(Base):
    __tablename__ = "risk_cases"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False, index=True
    )
    assigned_analyst_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default=CaseStatus.OPEN.value, index=True
    )
    priority: Mapped[str] = mapped_column(
        String(50), nullable=False, default=CasePriority.MEDIUM.value, index=True
    )
    risk_score: Mapped[int] = mapped_column(Integer, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False
    )
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_cases")
    assigned_analyst: Mapped[Optional["User"]] = relationship("User", back_populates="assigned_cases")
    analyst_actions: Mapped[List["AnalystAction"]] = relationship(
        "AnalystAction", back_populates="risk_case", cascade="all, delete-orphan"
    )


class AnalystAction(Base):
    __tablename__ = "analyst_actions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_case_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("risk_cases.id", ondelete="CASCADE"), nullable=False, index=True
    )
    analyst_id: Mapped[Optional[int]] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True
    )
    action_type: Mapped[str] = mapped_column(String(50), nullable=False)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    previous_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    risk_case: Mapped["RiskCase"] = relationship("RiskCase", back_populates="analyst_actions")
    analyst: Mapped[Optional["User"]] = relationship("User", back_populates="analyst_actions")
