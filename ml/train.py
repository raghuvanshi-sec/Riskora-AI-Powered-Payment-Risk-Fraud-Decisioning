#!/usr/bin/env python
"""Standalone ML model training script.

Run this script to train the ML model on the current database:
    uv run python -m ml.train

The script will:
1. Load all transactions from the database
2. Generate synthetic labels (for development)
3. Train an XGBoost model
4. Register and persist the model
5. Print evaluation metrics

IMPORTANT: This uses SYNTHETIC labels for development.
Do NOT present the resulting metrics as real-world fraud detection performance.
"""

import argparse
import logging
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Train ML risk model")
    parser.add_argument("--version", default="ml-v1", help="Model version tag")
    parser.add_argument("--fraud-rate", type=float, default=0.12, help="Synthetic fraud rate")
    parser.add_argument("--n-estimators", type=int, default=100, help="Number of XGBoost estimators")
    parser.add_argument("--max-depth", type=int, default=6, help="Max tree depth")
    parser.add_argument("--learning-rate", type=float, default=0.1, help="Learning rate")
    args = parser.parse_args()

    try:
        from .training import TrainingConfig, train_from_dataset
        from .models import ModelRegistry
        from app.db.database import SessionLocal
        from app.models.transaction import Transaction
    except ImportError as e:
        logger.error(f"Import error: {e}")
        logger.error("Make sure sklearn and xgboost are installed: pip install scikit-learn xgboost")
        sys.exit(1)

    db = SessionLocal()
    try:
        transactions = db.query(Transaction).all()
        if not transactions:
            logger.error("No transactions found in database. Seed data first.")
            sys.exit(1)

        tx_dicts = []
        for tx in transactions:
            tx_dicts.append({
                "amount": tx.amount,
                "account_age_days": tx.account_age_days,
                "previous_transaction_amount": tx.previous_transaction_amount,
                "transaction_frequency": tx.transaction_frequency,
                "failed_attempts": tx.failed_attempts,
                "device_change": tx.device_change,
                "location_change": tx.location_change,
                "merchant_risk": tx.merchant_risk,
                "velocity": tx.velocity,
            })

        logger.info(f"Loaded {len(tx_dicts)} transactions from database")

        import numpy as np
        np.random.seed(42)
        labels = np.random.binomial(1, args.fraud_rate, len(tx_dicts)).tolist()

        config = TrainingConfig(
            n_estimators=args.n_estimators,
            max_depth=args.max_depth,
            learning_rate=args.learning_rate,
        )

        logger.info(f"Training model version={args.version} with synthetic labels")
        result = train_from_dataset(tx_dicts, labels, config=config, version=args.version)

        logger.info("=" * 60)
        logger.info(f"Training complete: {result.version}")
        logger.info(f"Algorithm: {result.algorithm}")
        logger.info(f"Training samples: {result.training_samples}")
        logger.info(f"Test samples: {result.test_samples}")
        logger.info("Metrics:")
        for k, v in result.metrics.items():
            logger.info(f"  {k}: {v:.4f}")
        logger.info("Feature importance:")
        for name, imp in sorted(result.feature_importance.items(), key=lambda x: -x[1])[:5]:
            logger.info(f"  {name}: {imp:.4f}")
        logger.info("=" * 60)
        logger.info("Model registered and set as active.")

        active = ModelRegistry.get_active()
        if active:
            logger.info(f"Active model: {active.version}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
