from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class CaseCreate(BaseModel):
    transaction_id: int
    priority: str = Field(default="MEDIUM")
    summary: Optional[str] = None


class CaseUpdate(BaseModel):
    status: Optional[str] = None
    priority: Optional[str] = None
    assigned_analyst_id: Optional[int] = None
    summary: Optional[str] = None
    internal_notes: Optional[str] = None


class CaseAssign(BaseModel):
    assigned_analyst_id: int


class CaseResponse(BaseModel):
    id: int
    transaction_id: int
    assigned_analyst_id: Optional[int]
    status: str
    priority: str
    risk_score: int
    risk_level: str
    decision: str
    summary: Optional[str]
    internal_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]

    class Config:
        from_attributes = True


class CaseListResponse(BaseModel):
    id: int
    transaction_id: int
    status: str
    priority: str
    risk_score: int
    risk_level: str
    decision: str
    summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseDetailResponse(BaseModel):
    id: int
    transaction_id: int
    assigned_analyst_id: Optional[int]
    status: str
    priority: str
    risk_score: int
    risk_level: str
    decision: str
    summary: Optional[str]
    internal_notes: Optional[str]
    created_at: datetime
    updated_at: datetime
    resolved_at: Optional[datetime]
    transaction: Optional[dict] = None
    analyst_actions: Optional[List[dict]] = None

    class Config:
        from_attributes = True


class AnalystActionCreate(BaseModel):
    action_type: str
    reason: Optional[str] = None
    new_status: Optional[str] = None
    metadata: Optional[str] = None


class AnalystActionResponse(BaseModel):
    id: int
    risk_case_id: int
    analyst_id: Optional[int]
    action_type: str
    reason: Optional[str]
    previous_status: Optional[str]
    new_status: Optional[str]
    metadata: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class PaginatedCasesResponse(BaseModel):
    items: List[CaseListResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PaginatedActionsResponse(BaseModel):
    items: List[AnalystActionResponse]
    total: int
    page: int
    page_size: int
    pages: int
