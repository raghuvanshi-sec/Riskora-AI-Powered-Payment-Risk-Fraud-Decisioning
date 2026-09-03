"""
Risk Persistence Service
========================

Handles database operations for risk assessments, risk events,
triggered rules, and SHAP features.

Does NOT perform ML inference - that lives in ieee_risk_service.
"""

import logging
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from app.models.risk import RiskAssessment, RiskEvent
from app.models.ieee_risk import TriggeredRule, SHAPFeature
from app.models.transaction import Transaction
from app.services.audit_service import log_audit


logger = logging.getLogger(__name__)


def get_transaction(db: Session, transaction_id: int) -> Optional[Transaction]:
    """Get a transaction by ID."""
    return db.query(Transaction).filter(Transaction.id == transaction_id).first()


def create_risk_assessment(
    db: Session,
    transaction_id: int,
    inference_result: Dict[str, Any],
    user_id: Optional[int] = None,
) -> Tuple[RiskAssessment, List[TriggeredRule], List[SHAPFeature]]:
    """
    Persist a risk assessment from inference results.

    Args:
        db: Database session
        transaction_id: The transaction being assessed
        inference_result: Dict from ieee_risk_service.assess()
        user_id: Optional user performing the assessment

    Returns:
        Tuple of (RiskAssessment, list of TriggeredRule, list of SHAPFeature)

    Raises:
        ValueError: If transaction doesn't exist
    """
    transaction = get_transaction(db, transaction_id)
    if not transaction:
        raise ValueError(f"Transaction with id={transaction_id} not found")

    risk_score_int = int(round(inference_result["risk_score"]))

    assessment = RiskAssessment(
        transaction_id=transaction_id,
        risk_score=risk_score_int,
        risk_level=inference_result["risk_level"],
        decision=inference_result["decision"],
        explanation=inference_result.get("explanation"),
        model_version=inference_result.get("model_version"),
        preprocessor_version=inference_result.get("preprocessor_version"),
        ml_probability=inference_result.get("ml_probability"),
        ml_score=inference_result.get("ml_score"),
        rule_score=inference_result.get("rule_score"),
    )
    db.add(assessment)
    db.flush()

    triggered_rules = []
    for rule_data in inference_result.get("triggered_rules", []):
        rule = TriggeredRule(
            risk_assessment_id=assessment.id,
            rule_id=rule_data.get("rule_id", ""),
            name=rule_data.get("name", ""),
            severity=rule_data.get("severity", "LOW"),
            score_contribution=rule_data.get("score_contribution", 0),
            reason=rule_data.get("reason"),
            triggered=bool(rule_data.get("triggered", False)),
        )
        db.add(rule)
        triggered_rules.append(rule)

    shap_features = []
    for feat_data in inference_result.get("top_positive_features", []):
        shap_feat = SHAPFeature(
            risk_assessment_id=assessment.id,
            feature_name=feat_data.get("feature_name", ""),
            shap_value=feat_data.get("shap_value", 0.0),
            direction=feat_data.get("direction", "increases_risk"),
        )
        db.add(shap_feat)
        shap_features.append(shap_feat)

    for feat_data in inference_result.get("top_negative_features", []):
        shap_feat = SHAPFeature(
            risk_assessment_id=assessment.id,
            feature_name=feat_data.get("feature_name", ""),
            shap_value=feat_data.get("shap_value", 0.0),
            direction=feat_data.get("direction", "decreases_risk"),
        )
        db.add(shap_feat)
        shap_features.append(shap_feat)

    log_audit(
        db,
        action="RISK_ASSESSMENT_CREATED",
        entity_type="RISK_ASSESSMENT",
        entity_id=str(assessment.id),
        user_id=user_id,
        details={
            "transaction_id": transaction_id,
            "risk_score": risk_score_int,
            "risk_level": inference_result["risk_level"],
            "decision": inference_result["decision"],
            "model_version": inference_result.get("model_version"),
        },
    )

    return assessment, triggered_rules, shap_features


def create_risk_event(
    db: Session,
    transaction_id: int,
    event_type: str,
    description: Optional[str] = None,
    severity: str = "INFO",
    user_id: Optional[int] = None,
) -> RiskEvent:
    """
    Create a risk event record.

    Common event types:
    - RISK_ASSESSED
    - RISK_LEVEL_CHANGED
    - RISK_DECISION_MADE
    - MANUAL_REVIEW
    """
    event = RiskEvent(
        transaction_id=transaction_id,
        event_type=event_type,
        description=description,
        severity=severity,
    )
    db.add(event)
    db.flush()

    log_audit(
        db,
        action=f"RISK_EVENT_{event_type}",
        entity_type="RISK_EVENT",
        entity_id=str(event.id),
        user_id=user_id,
        details={
            "transaction_id": transaction_id,
            "event_type": event_type,
            "severity": severity,
        },
    )

    return event


def get_latest_risk_assessment(
    db: Session, transaction_id: int
) -> Optional[RiskAssessment]:
    """Get the most recent risk assessment for a transaction."""
    return (
        db.query(RiskAssessment)
        .options(
            selectinload(RiskAssessment.triggered_rules),
            selectinload(RiskAssessment.shap_features),
        )
        .filter(RiskAssessment.transaction_id == transaction_id)
        .order_by(desc(RiskAssessment.created_at))
        .first()
    )


def get_risk_assessment_with_relations(
    db: Session, assessment_id: int
) -> Optional[RiskAssessment]:
    """Get a risk assessment by ID with all relations loaded."""
    return (
        db.query(RiskAssessment)
        .options(
            selectinload(RiskAssessment.triggered_rules),
            selectinload(RiskAssessment.shap_features),
            selectinload(RiskAssessment.transaction),
        )
        .filter(RiskAssessment.id == assessment_id)
        .first()
    )


def get_risk_history(
    db: Session, transaction_id: int, limit: int = 10
) -> List[RiskAssessment]:
    """Get historical risk assessments for a transaction, newest first."""
    return (
        db.query(RiskAssessment)
        .options(
            selectinload(RiskAssessment.triggered_rules),
            selectinload(RiskAssessment.shap_features),
        )
        .filter(RiskAssessment.transaction_id == transaction_id)
        .order_by(desc(RiskAssessment.created_at))
        .limit(limit)
        .all()
    )


def get_risk_events(
    db: Session,
    transaction_id: int,
    limit: int = 50,
    event_type: Optional[str] = None,
) -> List[RiskEvent]:
    """Get risk events for a transaction."""
    q = db.query(RiskEvent).filter(RiskEvent.transaction_id == transaction_id)

    if event_type:
        q = q.filter(RiskEvent.event_type == event_type)

    return q.order_by(desc(RiskEvent.created_at)).limit(limit).all()
