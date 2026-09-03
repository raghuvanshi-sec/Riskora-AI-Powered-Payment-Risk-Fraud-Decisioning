import numpy as np
import pandas as pd
from typing import Optional, List
import math

from .constants import FEATURE_NAMES


def extract_features_from_transaction(
    amount: float,
    account_age_days: Optional[int],
    previous_transaction_amount: Optional[float],
    transaction_frequency: Optional[int],
    failed_attempts: Optional[int],
    device_change: Optional[bool],
    location_change: Optional[bool],
    merchant_risk: Optional[float],
    velocity: Optional[int],
) -> dict:
    amount_val = float(amount)
    prev_val = float(previous_transaction_amount) if previous_transaction_amount is not None else 0.0
    age_val = int(account_age_days) if account_age_days is not None else 0
    freq_val = int(transaction_frequency) if transaction_frequency is not None else 0
    attempts_val = int(failed_attempts) if failed_attempts is not None else 0
    device_val = 1 if device_change else 0
    location_val = 1 if location_change else 0
    merchant_val = float(merchant_risk) if merchant_risk is not None else 0.0
    velocity_val = int(velocity) if velocity is not None else 0

    amount_log = math.log1p(amount_val) if amount_val > 0 else 0.0
    amount_to_prev_ratio = (amount_val / prev_val) if prev_val > 0 else 0.0

    features = {
        "amount": amount_val,
        "account_age_days": age_val,
        "previous_transaction_amount": prev_val,
        "transaction_frequency": freq_val,
        "failed_attempts": attempts_val,
        "device_change": device_val,
        "location_change": location_val,
        "merchant_risk": merchant_val,
        "velocity": velocity_val,
        "amount_log": amount_log,
        "amount_to_prev_ratio": amount_to_prev_ratio,
        "is_high_amount": 1 if amount_val > 75000 else 0,
        "is_new_account": 1 if age_val < 30 else 0,
        "is_high_velocity": 1 if velocity_val > 6 else 0,
        "is_high_merchant_risk": 1 if merchant_val > 61 else 0,
    }

    return features


def transactions_to_feature_matrix(transactions: List[dict]) -> pd.DataFrame:
    rows = []
    for tx in transactions:
        features = extract_features_from_transaction(
            amount=tx.get("amount", 0),
            account_age_days=tx.get("account_age_days"),
            previous_transaction_amount=tx.get("previous_transaction_amount"),
            transaction_frequency=tx.get("transaction_frequency"),
            failed_attempts=tx.get("failed_attempts"),
            device_change=tx.get("device_change"),
            location_change=tx.get("location_change"),
            merchant_risk=tx.get("merchant_risk"),
            velocity=tx.get("velocity"),
        )
        rows.append(features)

    df = pd.DataFrame(rows)
    for col in FEATURE_NAMES:
        if col not in df.columns:
            df[col] = 0
    df = df[FEATURE_NAMES]
    df = df.fillna(0)
    return df


def get_feature_names() -> List[str]:
    return list(FEATURE_NAMES)


def validate_features(features: dict) -> bool:
    for name in FEATURE_NAMES:
        if name not in features:
            return False
        val = features[name]
        if val is None:
            return False
        if not isinstance(val, (int, float)):
            return False
    return True
