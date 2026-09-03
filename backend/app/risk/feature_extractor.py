from dataclasses import dataclass
from typing import Optional


@dataclass
class TransactionSignals:
    amount: float
    currency: str
    previous_transaction_amount: Optional[float]
    transaction_frequency: Optional[int]
    failed_attempts: Optional[int]
    device_change: Optional[bool]
    location_change: Optional[bool]
    merchant_risk: Optional[float]
    velocity: Optional[int]
    account_age_days: Optional[int]
    device_id: Optional[str]
    location: Optional[str]


def extract_signals(
    amount: float,
    currency: str,
    previous_transaction_amount: Optional[float],
    transaction_frequency: Optional[int],
    failed_attempts: Optional[int],
    device_change: Optional[bool],
    location_change: Optional[bool],
    merchant_risk: Optional[float],
    velocity: Optional[int],
    account_age_days: Optional[int],
    device_id: Optional[str],
    location: Optional[str],
) -> TransactionSignals:
    return TransactionSignals(
        amount=amount,
        currency=currency,
        previous_transaction_amount=previous_transaction_amount,
        transaction_frequency=transaction_frequency,
        failed_attempts=failed_attempts,
        device_change=device_change,
        location_change=location_change,
        merchant_risk=merchant_risk,
        velocity=velocity,
        account_age_days=account_age_days,
        device_id=device_id,
        location=location,
    )
