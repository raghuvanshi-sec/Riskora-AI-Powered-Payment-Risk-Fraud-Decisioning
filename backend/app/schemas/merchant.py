from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime

class MerchantBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    category: str = Field(..., min_length=2, max_length=100)
    risk_level: str = Field("LOW", max_length=50) # LOW, MEDIUM, HIGH
    is_active: bool = True

class MerchantCreate(MerchantBase):
    pass

class MerchantResponse(MerchantBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
