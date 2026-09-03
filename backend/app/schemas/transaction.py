from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List, Generic, TypeVar
from enum import Enum

# --- Enums ---

class CurrencyEnum(str, Enum):
    INR = "INR"

class SortOrderEnum(str, Enum):
    asc = "asc"
    desc = "desc"

# --- Nested response schemas ---

class UserBrief(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class MerchantBrief(BaseModel):
    id: int
    name: str
    category: str

    model_config = ConfigDict(from_attributes=True)

# --- Base ---

class TransactionBase(BaseModel):
    transaction_reference: str = Field(..., max_length=100)
    user_id: int
    merchant_id: int
    amount: float = Field(..., ge=0)
    currency: str = Field("INR", max_length=10)
    device_id: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    transaction_timestamp: datetime
    account_age_days: Optional[int] = Field(None, ge=0)
    previous_transaction_amount: Optional[float] = Field(None, ge=0)
    transaction_frequency: Optional[int] = Field(None, ge=0)
    failed_attempts: Optional[int] = Field(None, ge=0)
    device_change: Optional[bool] = False
    location_change: Optional[bool] = False
    merchant_risk: Optional[float] = Field(None, ge=0, le=100)
    velocity: Optional[int] = Field(None, ge=0)

# --- Create ---

class TransactionCreate(TransactionBase):
    pass

# --- Update (partial) ---

class TransactionUpdate(BaseModel):
    """Only fields that are legitimately mutable."""
    device_id: Optional[str] = Field(None, max_length=100)
    location: Optional[str] = Field(None, max_length=100)
    account_age_days: Optional[int] = Field(None, ge=0)
    previous_transaction_amount: Optional[float] = Field(None, ge=0)
    transaction_frequency: Optional[int] = Field(None, ge=0)
    failed_attempts: Optional[int] = Field(None, ge=0)
    device_change: Optional[bool] = None
    location_change: Optional[bool] = None
    merchant_risk: Optional[float] = Field(None, ge=0, le=100)
    velocity: Optional[int] = Field(None, ge=0)

# --- Response ---

class TransactionResponse(BaseModel):
    id: int
    transaction_reference: str
    user: UserBrief
    merchant: MerchantBrief
    amount: float
    currency: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    transaction_timestamp: datetime
    account_age_days: Optional[int] = None
    previous_transaction_amount: Optional[float] = None
    transaction_frequency: Optional[int] = None
    failed_attempts: Optional[int] = None
    device_change: Optional[bool] = None
    location_change: Optional[bool] = None
    merchant_risk: Optional[float] = None
    velocity: Optional[int] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    decision: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class TransactionListItem(BaseModel):
    """Lighter schema for list views — no deep nested objects."""
    id: int
    transaction_reference: str
    user: UserBrief
    merchant: MerchantBrief
    amount: float
    currency: str
    location: Optional[str] = None
    transaction_timestamp: datetime
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    decision: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Pagination (generic, reusable) ---

T = TypeVar("T")

class PaginatedResponse(BaseModel, Generic[T]):
    items: List[T]
    page: int
    page_size: int
    total: int
    total_pages: int

# --- Summary ---

class TransactionSummary(BaseModel):
    total_transactions: int
    total_amount: float
    today_transactions: int
    today_amount: float

# --- Detail (nested risk assessments + events) ---

from .risk import RiskAssessmentResponse, RiskEventResponse

class TransactionDetail(BaseModel):
    """Full transaction view including nested risk assessments and events."""
    id: int
    transaction_reference: str
    user: UserBrief
    merchant: MerchantBrief
    amount: float
    currency: str
    device_id: Optional[str] = None
    location: Optional[str] = None
    transaction_timestamp: datetime
    account_age_days: Optional[int] = None
    previous_transaction_amount: Optional[float] = None
    transaction_frequency: Optional[int] = None
    failed_attempts: Optional[int] = None
    device_change: Optional[bool] = None
    location_change: Optional[bool] = None
    merchant_risk: Optional[float] = None
    velocity: Optional[int] = None
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    decision: Optional[str] = None
    created_at: datetime
    risk_assessments: List[RiskAssessmentResponse] = []
    risk_events: List[RiskEventResponse] = []

    model_config = ConfigDict(from_attributes=True)
