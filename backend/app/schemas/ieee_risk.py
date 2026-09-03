"""
IEEE-CIS Risk Assessment Schemas
==============================

Pydantic schemas for IEEE-CIS based risk assessment API.
"""

from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any


class IEEETransactionInput(BaseModel):
    """IEEE-CIS style transaction input for risk assessment."""

    TransactionAmt: float = Field(..., gt=0, description="Transaction amount")
    TransactionDT: float = Field(..., ge=0, description="Transaction timestamp")

    ProductCD: Optional[str] = Field(None, description="Product code")

    card1: Optional[float] = Field(None, description="Card field 1")
    card2: Optional[float] = Field(None, description="Card field 2")
    card3: Optional[float] = Field(None, description="Card field 3")
    card4: Optional[str] = Field(None, description="Card field 4")
    card5: Optional[float] = Field(None, description="Card field 5")
    card6: Optional[str] = Field(None, description="Card field 6")

    addr1: Optional[float] = Field(None, description="Address field 1")
    addr2: Optional[float] = Field(None, description="Address field 2")

    P_emaildomain: Optional[str] = Field(None, description="Billing email domain")
    R_emaildomain: Optional[str] = Field(None, description="Recipient email domain")

    DeviceType: Optional[str] = Field(None, description="Device type")
    DeviceInfo: Optional[str] = Field(None, description="Device info")

    C1: Optional[float] = Field(None, description="Count feature 1")
    C2: Optional[float] = Field(None, description="Count feature 2")
    C3: Optional[float] = Field(None, description="Count feature 3")
    C4: Optional[float] = Field(None, description="Count feature 4")
    C5: Optional[float] = Field(None, description="Count feature 5")
    C6: Optional[float] = Field(None, description="Count feature 6")
    C7: Optional[float] = Field(None, description="Count feature 7")
    C8: Optional[float] = Field(None, description="Count feature 8")
    C9: Optional[float] = Field(None, description="Count feature 9")
    C10: Optional[float] = Field(None, description="Count feature 10")
    C11: Optional[float] = Field(None, description="Count feature 11")
    C12: Optional[float] = Field(None, description="Count feature 12")
    C13: Optional[float] = Field(None, description="Count feature 13")
    C14: Optional[float] = Field(None, description="Count feature 14")

    D1: Optional[float] = Field(None, description="Day feature 1")
    D2: Optional[float] = Field(None, description="Day feature 2")
    D3: Optional[float] = Field(None, description="Day feature 3")
    D4: Optional[float] = Field(None, description="Day feature 4")
    D5: Optional[float] = Field(None, description="Day feature 5")
    D6: Optional[float] = Field(None, description="Day feature 6")
    D7: Optional[float] = Field(None, description="Day feature 7")
    D8: Optional[float] = Field(None, description="Day feature 8")
    D9: Optional[float] = Field(None, description="Day feature 9")
    D10: Optional[float] = Field(None, description="Day feature 10")
    D11: Optional[float] = Field(None, description="Day feature 11")
    D12: Optional[float] = Field(None, description="Day feature 12")
    D13: Optional[float] = Field(None, description="Day feature 13")
    D14: Optional[float] = Field(None, description="Day feature 14")
    D15: Optional[float] = Field(None, description="Day feature 15")

    M1: Optional[str] = Field(None, description="Match feature 1")
    M2: Optional[str] = Field(None, description="Match feature 2")
    M3: Optional[str] = Field(None, description="Match feature 3")
    M4: Optional[str] = Field(None, description="Match feature 4")
    M5: Optional[str] = Field(None, description="Match feature 5")
    M6: Optional[str] = Field(None, description="Match feature 6")
    M7: Optional[str] = Field(None, description="Match feature 7")
    M8: Optional[str] = Field(None, description="Match feature 8")
    M9: Optional[str] = Field(None, description="Match feature 9")

    V1: Optional[float] = Field(None, description="VFeature 1")
    V2: Optional[float] = Field(None, description="VFeature 2")
    V3: Optional[float] = Field(None, description="VFeature 3")
    V4: Optional[float] = Field(None, description="VFeature 4")
    V5: Optional[float] = Field(None, description="VFeature 5")
    V6: Optional[float] = Field(None, description="VFeature 6")
    V7: Optional[float] = Field(None, description="VFeature 7")
    V8: Optional[float] = Field(None, description="VFeature 8")
    V9: Optional[float] = Field(None, description="VFeature 9")
    V10: Optional[float] = Field(None, description="VFeature 10")

    model_config = ConfigDict(extra="allow")


class TriggeredRule(BaseModel):
    """A triggered rule in the risk assessment."""
    rule_id: str
    name: str
    severity: str
    score_contribution: int
    triggered: bool
    reason: str


class SHAPFeature(BaseModel):
    """A SHAP feature contribution."""
    feature_name: str
    shap_value: float
    direction: str


class IEEERiskAssessmentResponse(BaseModel):
    """Response schema for IEEE-CIS risk assessment."""

    risk_score: float = Field(..., ge=0, le=100)
    risk_level: str = Field(..., pattern="^(LOW|MEDIUM|HIGH)$")
    decision: str = Field(..., pattern="^(ALLOW|REVIEW|BLOCK)$")

    ml_probability: float = Field(..., ge=0, le=1)
    ml_score: float = Field(..., ge=0, le=100)
    rule_score: float = Field(..., ge=0, le=100)

    triggered_rules: List[TriggeredRule] = Field(default_factory=list)
    rule_reasons: List[str] = Field(default_factory=list)

    top_positive_features: List[SHAPFeature] = Field(default_factory=list)
    top_negative_features: List[SHAPFeature] = Field(default_factory=list)

    explanation: str

    model_version: str
    preprocessor_version: str

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IEEERiskHealthResponse(BaseModel):
    """Health check response for IEEE risk engine."""
    status: str
    model_loaded: bool
    preprocessor_loaded: bool
    model_version: Optional[str] = None
    preprocessor_version: Optional[str] = None
    model_config = ConfigDict(protected_namespaces=())


class IEEERiskAssessmentCreate(BaseModel):
    """Request schema for creating a persisted risk assessment."""
    transaction_id: int = Field(..., description="ID of the transaction to assess")
    persist: bool = Field(
        default=True,
        description="Whether to persist the assessment (default True)"
    )


class IEEERiskAssessmentDBResponse(BaseModel):
    """Response schema for persisted risk assessment from database."""
    id: int
    transaction_id: int
    risk_score: int
    risk_level: str
    decision: str
    explanation: Optional[str] = None
    model_version: Optional[str] = None
    preprocessor_version: Optional[str] = None
    ml_probability: Optional[float] = None
    ml_score: Optional[float] = None
    rule_score: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IEEERiskAssessmentFullResponse(BaseModel):
    """Full response schema for persisted risk assessment with all details."""
    id: int
    transaction_id: int
    risk_score: int
    risk_level: str
    decision: str
    explanation: Optional[str] = None
    model_version: Optional[str] = None
    preprocessor_version: Optional[str] = None
    ml_probability: Optional[float] = None
    ml_score: Optional[float] = None
    rule_score: Optional[float] = None
    triggered_rules: List[TriggeredRule] = Field(default_factory=list)
    rule_reasons: List[str] = Field(default_factory=list)
    top_positive_features: List[SHAPFeature] = Field(default_factory=list)
    top_negative_features: List[SHAPFeature] = Field(default_factory=list)
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IEEERiskHistoryItem(BaseModel):
    """Single item in risk history."""
    id: int
    risk_score: int
    risk_level: str
    decision: str
    ml_probability: Optional[float] = None
    ml_score: Optional[float] = None
    rule_score: Optional[float] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IEEERiskHistoryResponse(BaseModel):
    """Response schema for risk assessment history."""
    transaction_id: int
    assessments: List[IEEERiskHistoryItem]
    total: int


class IEEERiskEventResponse(BaseModel):
    """Response schema for risk events."""
    id: int
    transaction_id: int
    event_type: str
    description: Optional[str] = None
    severity: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class IEEERiskEventsResponse(BaseModel):
    """Response schema for list of risk events."""
    transaction_id: int
    events: List[IEEERiskEventResponse]
    total: int
