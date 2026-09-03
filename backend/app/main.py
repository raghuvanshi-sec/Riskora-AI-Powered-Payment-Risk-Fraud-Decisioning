from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.core.config import settings
from app.core.errors import add_exception_handlers
from app.api.routes import api_router
from app.db.database import engine
from app.db.base import Base

app = FastAPI(
    title="AI Risk Manager API",
    description="Payment risk and fraud decisioning platform API",
    version="1.0.0",
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add structured exception handlers
add_exception_handlers(app)

# Include API routes
app.include_router(api_router, prefix=settings.API_V1_STR)

# Auto-create tables (SQLite file) on startup so the app is usable without
# running a separate migration/seed step. No-op for existing databases.
Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def _maybe_seed_database() -> None:
    """Seed the admin user + synthetic transactions on first run."""
    from sqlalchemy.orm import Session
    from app.db.database import SessionLocal
    from app.models.user import User
    from app.core.security import get_password_hash
    from app.db.seed_transactions import generate_transactions

    db = SessionLocal()
    try:
        if not db.query(User).first():
            admin = User(
                email="admin@airiskmanager.com",
                password_hash=get_password_hash("RiskoraDemo123!"),
                name="Admin User",
                is_active=True,
                role="ADMIN",
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
        generate_transactions(db)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("Seed skipped: %s", e)
        db.rollback()
    finally:
        db.close()

@app.get("/health", tags=["health"])
async def health_check_root():
    """
    Health check endpoint (root level).
    """
    return {"status": "ok", "service": "ai-risk-manager-api"}


@app.get(f"{settings.API_V1_STR}/health", tags=["health"])
async def health_check():
    """
    Health check endpoint (versioned).
    """
    return {"status": "ok", "service": "ai-risk-manager-api"}

from fastapi import Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import get_db

@app.get(f"{settings.API_V1_STR}/health/db", tags=["health"])
async def health_check_db(db: Session = Depends(get_db)):
    """
    Database health check endpoint.
    """
    try:
        # Execute a simple query to check the database connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        return {"status": "error", "database": "disconnected", "details": str(e)}


# ── Optional: serve the built frontend (frontend/dist) from the API server ──
# This gives a single origin (http://<host>:8000) with full SPA routing and deep-link
# fallback, so the sidebar/app routes also work in production/static contexts (no CORS,
# no "404 on refresh"). If the Vite build is absent (dev mode via `npm run dev`),
# the API-only behavior is preserved.
FRONTEND_DIST = Path(__file__).resolve().parents[2] / "frontend" / "dist"

if FRONTEND_DIST.is_dir():
    assets_dir = FRONTEND_DIST / "assets"
    if assets_dir.is_dir():
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        """Serve Vite build assets with SPA fallback to index.html (except API routes)."""
        if full_path == "api" or full_path.startswith("api/"):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = FRONTEND_DIST / full_path
        if full_path and candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(FRONTEND_DIST / "index.html")
