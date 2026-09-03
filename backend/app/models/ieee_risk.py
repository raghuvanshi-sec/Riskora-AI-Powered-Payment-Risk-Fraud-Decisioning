from sqlalchemy import String, DateTime, Integer, Float, Text, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from typing import Optional, List
from app.db.database import Base


class TriggeredRule(Base):
    __tablename__ = "triggered_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_assessment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("risk_assessments.id", ondelete="CASCADE"), nullable=False
    )
    rule_id: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    severity: Mapped[str] = mapped_column(String(50), nullable=False, default="LOW")
    score_contribution: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    triggered: Mapped[bool] = mapped_column(Integer, nullable=False, default=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    risk_assessment: Mapped["RiskAssessment"] = relationship(
        "RiskAssessment", back_populates="triggered_rules"
    )


class SHAPFeature(Base):
    __tablename__ = "shap_features"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    risk_assessment_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("risk_assessments.id", ondelete="CASCADE"), nullable=False
    )
    feature_name: Mapped[str] = mapped_column(String(255), nullable=False)
    shap_value: Mapped[float] = mapped_column(Float, nullable=False)
    direction: Mapped[str] = mapped_column(String(50), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    risk_assessment: Mapped["RiskAssessment"] = relationship(
        "RiskAssessment", back_populates="shap_features"
    )
