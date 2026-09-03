from sqlalchemy import String, DateTime, Integer, Float, Text, ForeignKey, CheckConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from app.db.database import Base


class RiskAssessment(Base):
    __tablename__ = "risk_assessments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    risk_score: Mapped[int] = mapped_column(Integer, index=True, nullable=False)
    risk_level: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    decision: Mapped[str] = mapped_column(String(50), nullable=False)
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    ml_probability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    ml_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rule_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    preprocessor_version: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    __table_args__ = (
        CheckConstraint("risk_score >= 0 AND risk_score <= 100", name="check_risk_score_range"),
    )

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_assessments")
    triggered_rules: Mapped[List["TriggeredRule"]] = relationship(
        "TriggeredRule", back_populates="risk_assessment", cascade="all, delete-orphan"
    )
    shap_features: Mapped[List["SHAPFeature"]] = relationship(
        "SHAPFeature", back_populates="risk_assessment", cascade="all, delete-orphan"
    )


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaction_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("transactions.id", ondelete="CASCADE"), nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="INFO")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    transaction: Mapped["Transaction"] = relationship("Transaction", back_populates="risk_events")


from app.models.ieee_risk import TriggeredRule, SHAPFeature
