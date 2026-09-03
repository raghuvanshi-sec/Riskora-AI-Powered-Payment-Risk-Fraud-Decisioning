from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional

# RiskAssessment Schemas
class RiskAssessmentBase(BaseModel):
    transaction_id: int
    risk_score: int = Field(..., ge=0, le=100) # Must be between 0 and 100
    risk_level: str = Field(..., max_length=50) # LOW, MEDIUM, HIGH
    decision: str = Field(..., max_length=50) # ALLOW, REVIEW, BLOCK
    explanation: Optional[str] = None
    model_version: Optional[str] = Field(None, max_length=50)

class RiskAssessmentCreate(RiskAssessmentBase):
    pass

class RiskAssessmentResponse(RiskAssessmentBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# RiskEvent Schemas
class RiskEventBase(BaseModel):
    transaction_id: int
    event_type: str = Field(..., max_length=100)
    description: Optional[str] = None
    severity: str = Field("INFO", max_length=50)

class RiskEventCreate(RiskEventBase):
    pass

class RiskEventResponse(RiskEventBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
