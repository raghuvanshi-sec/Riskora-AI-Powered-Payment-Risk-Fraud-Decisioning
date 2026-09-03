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
