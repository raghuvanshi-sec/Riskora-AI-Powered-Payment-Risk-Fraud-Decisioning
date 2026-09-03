"""Deterministic synthetic transaction generator.

Seeds fictional customers (User rows) and merchants (Merchant rows) plus
100-300 Transaction rows referencing them. Uses random.seed(42) so the
generated dataset is reproducible across runs.

Risk scoring is intentionally NOT performed — risk_score/risk_level/decision
remain NULL. This generator only produces raw transaction data.
"""

import logging
import random
from datetime import datetime, timedelta
from typing import Tuple

from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.merchant import Merchant
from app.models.user import User

logger = logging.getLogger(__name__)

# Default password for all seeded fictional accounts. Documented so the
# demo login flow is reproducible; never real credentials.
SEEDED_PASSWORD = "RiskoraDemo123!"

FIRST_NAMES = [
    "Aarav", "Vikram", "Preeti", "Rajesh", "Siddharth", "Ananya", "Karan", "Meera",
    "Rohit", "Sneha", "Arjun", "Priya", "Aditya", "Neha", "Kabir", "Diya",
    "Sahil", "Ishita", "Mantra", "Tanya", "Veer", "Riya", "Gaurav", "Simran",
    "Nikhil", "Pooja", "Varun", "Kriti", "Harsh", "Aisha",
]

LAST_NAMES = [
    "Sharma", "Malhotra", "Patel", "Kumar", "Rao", "Verma", "Gupta", "Singh",
    "Jain", "Reddy", "Nair", "Menon", "Das", "Chopra", "Agarwal", "Iyer",
    "Bhatia", "Choudhury", "Mishra", "Desai", "Kapoor", "Bose", "Nanda", "Sarin",
]

MERCHANT_NAMES = [
    "Amazon India", "Flipkart", "Swiggy", "Zomato Dineout", "MakeMyTrip",
    "Apple Store IN", "Reliance Digital", "Croma", "Myntra", "Ajio",
    "BigBasket", "Zepto", "Blinkit", "PhonePe", "Google Play IN",
    "Steam Games", "BookMyShow", "Nykaa", "Boat", " Mamaearth",
    "Uber India", "Ola", "IRCTC", "Netflix IN", "Spotify IN",
]

MERCHANT_CATEGORIES = [
    "E-commerce", "Food & Beverage", "Travel", "Electronics", "Fashion",
    "Grocery", "Ride-hailing", "Tickets", "Beauty", "Gaming",
    "Music Streaming", "Video Streaming", "Digital Payments", "Entertainment",
]

LOCATIONS = [
    "Mumbai", "Delhi", "Bengaluru", "Hyderabad", "Chennai",
    "Kolkata", "Pune", "Ahmedabad", "Jaipur", "Lucknow",
    "Indore", "Nagpur", "Bhopal", "Surat", "Coimbatore",
]

DEVICES = [
    "iPhone-14-Pro", "iPhone-13", "Samsung-S23", "Pixel-8", "OnePlus-12",
    "Xiaomi-13", "iPhone-15", "Samsung-S24", "Google-Pixel-7", "OnePlus-11",
]


def _create_fictional_users(db: Session, count: int = 20) -> list[User]:
    from app.core.security import get_password_hash

    users = []
    for i in range(count):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        email = f"customer{i+1:02d}@airiskmanager.local"
        user = User(
            name=name,
            email=email,
            password_hash=get_password_hash(SEEDED_PASSWORD),
            role="USER",
            is_active=True,
        )
        db.add(user)
        users.append(user)
    db.flush()
    return users


def _create_fictional_merchants(db: Session, count: int = 20) -> list[Merchant]:
    merchants = []
    for i in range(count):
        merchant = Merchant(
            name=MERCHANT_NAMES[i % len(MERCHANT_NAMES)],
            category=MERCHANT_CATEGORIES[i % len(MERCHANT_CATEGORIES)],
            risk_level=random.choice(["LOW", "MEDIUM", "HIGH"]),
            is_active=True,
        )
        db.add(merchant)
        merchants.append(merchant)
    db.flush()
    return merchants


def generate_transactions(db: Session, target: int = 200) -> int:
    """Seed fictional customers, merchants, and transactions.

    Returns the number of transactions created. Idempotent: if transactions
    already exist, returns 0 without duplicating.
    """
    existing = db.query(Transaction).first()
    if existing:
        logger.info("Transactions already seeded, skipping.")
        return 0

    random.seed(42)

    users = _create_fictional_users(db, count=20)
    merchants = _create_fictional_merchants(db, count=20)
    db.commit()

    # Flush to obtain PKs
    db.flush()

    now = datetime.now() - timedelta(days=1)
    end_date = now - timedelta(days=365)

    created = 0
    txns = []
    for i in range(target):
        user = random.choice(users)
        merchant = random.choice(merchants)
        amount = round(random.uniform(50, 250000), 2)

        # Deterministic timestamp spread across the last year
        ts = end_date + timedelta(
            days=random.randint(0, 365),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59),
            seconds=random.randint(0, 59),
        )

        # Deterministic flags — pure data, no scoring
        device_change = random.random() < 0.08
        location_change = random.random() < 0.1
        failed_attempts = random.choices([0, 1, 2, 3], weights=[85, 8, 5, 2])[0]
        velocity = random.choices([0, 1, 2, 5, 10], weights=[60, 20, 10, 7, 3])[0]

        txn = Transaction(
            transaction_reference=f"TX-{10000 + i}",
            user_id=user.id,
            merchant_id=merchant.id,
            amount=amount,
            currency="INR",
            device_id=random.choice(DEVICES),
            location=random.choice(LOCATIONS),
            transaction_timestamp=ts,
            account_age_days=random.randint(1, 1800),
            previous_transaction_amount=round(random.uniform(0, amount * 2), 2),
            transaction_frequency=random.randint(1, 30),
            failed_attempts=failed_attempts,
            device_change=device_change,
            location_change=location_change,
            merchant_risk=round(random.uniform(0, 100), 2),
            velocity=velocity,
            # risk_score / risk_level / decision intentionally NULL
        )
        txns.append(txn)

    db.add_all(txns)
    db.commit()

    for txn in txns:
        db.refresh(txn)

    created = len(txns)
    logger.info(f"Seeded {created} synthetic transactions.")

    from app.services.risk_service import analyze_transaction
    analyzed = 0
    for txn in txns:
        try:
            analyze_transaction(db, txn.id)
            analyzed += 1
        except Exception as e:
            logger.warning(f"Risk analysis failed for {txn.transaction_reference}: {e}")
    logger.info(f"Risk analysis completed for {analyzed} transactions.")

    return created