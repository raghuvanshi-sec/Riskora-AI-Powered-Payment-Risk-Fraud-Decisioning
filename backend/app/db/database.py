from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from typing import Generator
from app.core.config import settings

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent


def _resolve_sqlite_path(url: str) -> str:
    if url.startswith("sqlite:///./"):
        db_filename = url.replace("sqlite:///./", "")
        resolved_path = BACKEND_DIR / db_filename
        return f"sqlite:///{resolved_path.as_posix()}"
    return url


def _build_engine():
    url = settings.DATABASE_URL
    url = _resolve_sqlite_path(url)
    is_sqlite = url.startswith("sqlite")
    kwargs = {}
    if is_sqlite:
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_pre_ping"] = True
        kwargs["pool_size"] = 10
        kwargs["max_overflow"] = 20
    return create_engine(url, **kwargs)


engine = _build_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
