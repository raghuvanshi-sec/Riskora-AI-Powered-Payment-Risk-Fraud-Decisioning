from sqlalchemy import String, Boolean, DateTime, Integer, Float, func
from sqlalchemy.orm import Mapped, mapped_column
from datetime import datetime
from app.db.database import Base

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    version: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(100), nullable=False)
    algorithm: Mapped[str] = mapped_column(String(100), nullable=False)
    accuracy: Mapped[float] = mapped_column(Float, nullable=True)
    precision_score: Mapped[float] = mapped_column(Float, nullable=True)
    recall_score: Mapped[float] = mapped_column(Float, nullable=True)
    f1_score: Mapped[float] = mapped_column(Float, nullable=True)
    roc_auc: Mapped[float] = mapped_column(Float, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
