from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List


class RiskFactorResponse(BaseModel):
    code: str
    name: str
    description: str
    severity: str
    contribution: int

    model_config = ConfigDict(from_attributes=True)


class RiskAnalysisResponse(BaseModel):
    transaction_id: int
    risk_score: int
    risk_level: str
    decision: str
    explanation: str
    model_version: str
    risk_factors: List[RiskFactorResponse]

    model_config = ConfigDict(from_attributes=True)


class SHAPFactorResponse(BaseModel):
    feature_name: str
    feature_value: float
    contribution: float
    direction: str

    model_config = ConfigDict(from_attributes=True)


class ExplainableAnalysisResponse(BaseModel):
    transaction_id: int
    final_score: int
    final_level: str
    final_decision: str
    rules_score: int
    rules_level: str
    rules_decision: str
    ml_score: int
    ml_level: str
    ml_decision: str
    ml_probability: float
    rules_factors: List[RiskFactorResponse]
    shap_factors: List[SHAPFactorResponse]
    explanation: str
    rules_engine_version: str
    ml_model_version: str
    shap_available: bool
    inference_time_ms: Optional[float] = None
    feature_count: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class RiskSummaryResponse(BaseModel):
    total_assessed: int
    low: int
    medium: int
    high: int
    allowed: int
    review: int
    blocked: int


class RiskTrendItem(BaseModel):
    date: str
    low: int
    medium: int
    high: int


class RiskDecisionItem(BaseModel):
    transaction_id: int
    transaction_reference: str
    user_name: Optional[str]
    merchant_name: Optional[str]
    amount: float
    currency: str
    risk_score: int
    risk_level: str
    decision: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class RiskEventResponse(BaseModel):
    id: int
    transaction_id: int
    event_type: str
    description: Optional[str]
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SimulatorTransactionInput(BaseModel):
    amount: float = Field(..., gt=0, description="Transaction amount")
    currency: str = Field(default="INR", description="Currency code")
    payment_method: str = Field(default="card", description="Payment method")
    merchant_name: str = Field(default="Sample Merchant", description="Merchant name")
    transaction_type: str = Field(default="purchase", description="Transaction type")
    account_age_days: int = Field(default=365, ge=0, description="Account age in days")
    transactions_per_hour: int = Field(default=1, ge=0, description="Transactions per hour")
    failed_attempts: int = Field(default=0, ge=0, description="Failed payment attempts")
    device_changed: bool = Field(default=False, description="Device changed flag")
    location_changed: bool = Field(default=False, description="Location changed flag")
    merchant_risk: float = Field(default=0.3, ge=0, le=1, description="Merchant risk score 0-1")
