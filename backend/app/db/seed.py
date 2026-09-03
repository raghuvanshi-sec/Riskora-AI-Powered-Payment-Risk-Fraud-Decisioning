"""Seed entry point (manual).

Tables are auto-created on app startup via `app.main`, and the admin user
plus synthetic transactions are seeded then too. This script exists for
environments that need explicit seeding without booting the server.
"""

import logging
from sqlalchemy.orm import Session
from app.db.database import SessionLocal, engine
from app.db.base import Base
from app.models.user import User
from app.core.security import get_password_hash
from app.db.seed_transactions import generate_transactions

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Default password for all seeded accounts. Fictional users only — never
# real credentials. Documented so the demo login flow is reproducible.
SEEDED_PASSWORD = "RiskoraDemo123!"


def init_db(db: Session) -> None:
    Base.metadata.create_all(bind=engine)

    user = db.query(User).first()
    if not user:
        logger.info("Creating seed data...")
        admin = User(
            email="admin@airiskmanager.com",
            password_hash=get_password_hash(SEEDED_PASSWORD),
            name="Admin User",
            is_active=True,
            role="ADMIN",
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        logger.info("Admin user created (password: %s)", SEEDED_PASSWORD)
    else:
        logger.info("Database already seeded.")

    generate_transactions(db)


def main() -> None:
    logger.info("Creating initial data")
    db = SessionLocal()
    try:
        init_db(db)
    except Exception as e:
        logger.error(f"Error creating initial data: {e}")
    finally:
        db.close()
    logger.info("Initial data created")


if __name__ == "__main__":
    main()