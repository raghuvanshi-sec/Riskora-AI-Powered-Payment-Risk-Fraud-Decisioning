from sqlalchemy import String, Boolean, DateTime, Integer, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import List
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(50), nullable=False, default="RISK_ANALYST") # ADMIN, RISK_ANALYST
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # Relationships
    transactions: Mapped[List["Transaction"]] = relationship(
        "Transaction", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    audit_logs: Mapped[List["AuditLog"]] = relationship(
        "AuditLog", 
        back_populates="user", 
        cascade="all, delete-orphan"
    )
    assigned_cases: Mapped[List["RiskCase"]] = relationship(
        "RiskCase", 
        back_populates="assigned_analyst", 
        cascade="all, delete-orphan"
    )
    analyst_actions: Mapped[List["AnalystAction"]] = relationship(
        "AnalystAction", 
        back_populates="analyst", 
        cascade="all, delete-orphan"
    )
