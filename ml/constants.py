ML_MODEL_VERSION = "xgb-v1"
MODEL_ARTIFACTS_DIR = "artifacts"
FEATURE_NAMES = [
    "amount",
    "account_age_days",
    "previous_transaction_amount",
    "transaction_frequency",
    "failed_attempts",
    "device_change",
    "location_change",
    "merchant_risk",
    "velocity",
    "amount_log",
    "amount_to_prev_ratio",
    "is_high_amount",
    "is_new_account",
    "is_high_velocity",
    "is_high_merchant_risk",
]

FRAUD_PROBABILITY_THRESHOLD = 0.5
RISK_SCORE_MULTIPLIER = 100

HIGH_THRESHOLD = 0.7
MEDIUM_THRESHOLD = 0.3

TRAIN_TEST_SPLIT = 0.2
RANDOM_SEED = 42
