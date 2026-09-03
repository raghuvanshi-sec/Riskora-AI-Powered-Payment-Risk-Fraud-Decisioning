from pydantic import BaseModel, ConfigDict
from typing import Optional, Dict, Any
from datetime import datetime

class ModelVersionBase(BaseModel):
    version_tag: str
    description: Optional[str] = None
    is_active: bool = False
    parameters: Optional[Dict[str, Any]] = None

class ModelVersionCreate(ModelVersionBase):
    pass

class ModelVersionResponse(ModelVersionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
