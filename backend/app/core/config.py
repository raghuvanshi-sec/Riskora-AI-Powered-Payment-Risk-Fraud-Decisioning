import os
from typing import List, Union
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import AnyHttpUrl, validator

class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Risk Manager"
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # Security & Authentication
    SECRET_KEY: str = "supersecretjwtkeychangeinproduction1234567890!"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    
    # CORS Configuration
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = []

    @validator("BACKEND_CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    # Database Configuration
    # Defaults to a local SQLite file so the app runs without a live Postgres
    # instance. Override via the DATABASE_URL environment variable for prod.
    DATABASE_URL: str = "sqlite:///./airiskmanager.db"

    model_config = SettingsConfigDict(
        env_file=".env", 
        env_file_encoding="utf-8", 
        case_sensitive=True,
        extra="ignore" # Ignore extra env vars loaded from OS environment
    )

settings = Settings()
