import logging
from datetime import datetime, date
from typing import List, Optional, Tuple
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func, desc

logger = logging.getLogger(__name__)

from app.models.transaction import Transaction
from app.models.risk import RiskAssessment, RiskEvent
from app.risk.engine import RulesRiskEngine, RiskResult
from app.risk.feature_extractor import extract_signals
from app.risk import constants as C
from app.risk.rules import RiskFactor
from app.services.audit_service import log_audit

_ML_AVAILABLE = False
_HybridRiskEngine = None

try:
    from app.ml.hybrid import HybridRiskEngine as _HybridRiskEngine, HybridRiskResult
    from app.ml.models import ModelRegistry
    from app.ml.shap_explainer import explain_transaction
    _ML_AVAILABLE = True
except ImportError:
    _ML_AVAILABLE = False
    HybridRiskResult = None


def _get_hybrid_engine():
    if _ML_AVAILABLE and _HybridRiskEngine is not None:
        active = ModelRegistry.get_active()
        if active:
            return _HybridRiskEngine()
    return None


def analyze_transaction(db: Session, transaction_id: int, use_ml: bool = False) -> Optional[RiskAssessment]:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return None

    hybrid_engine = _get_hybrid_engine() if use_ml else None

    if hybrid_engine:
        result = hybrid_engine.analyze(
            amount=tx.amount,
            currency=tx.currency,
            previous_transaction_amount=tx.previous_transaction_amount,
            transaction_frequency=tx.transaction_frequency,
            failed_attempts=tx.failed_attempts,
            device_change=tx.device_change,
            location_change=tx.location_change,
            merchant_risk=tx.merchant_risk,
            velocity=tx.velocity,
            account_age_days=tx.account_age_days,
            device_id=tx.device_id,
            location=tx.location,
        )
        model_version = f"hybrid-{result.model_version}"
        risk_score = result.final_score
        risk_level = result.final_level
        decision = result.final_decision
        explanation = f"Hybrid analysis: rules score={result.rules_score}, ML score={result.ml_score}, final={result.final_score}"
        risk_factors = []
    else:
        signals = extract_signals(
            amount=tx.amount,
            currency=tx.currency,
            previous_transaction_amount=tx.previous_transaction_amount,
            transaction_frequency=tx.transaction_frequency,
            failed_attempts=tx.failed_attempts,
            device_change=tx.device_change,
            location_change=tx.location_change,
            merchant_risk=tx.merchant_risk,
            velocity=tx.velocity,
            account_age_days=tx.account_age_days,
            device_id=tx.device_id,
            location=tx.location,
        )
        engine = RulesRiskEngine()
        result = engine.analyze(signals)
        model_version = result.model_version
        risk_score = result.risk_score
        risk_level = result.risk_level
        decision = result.decision
        explanation = result.explanation
        risk_factors = result.risk_factors

    assessment = RiskAssessment(
        transaction_id=tx.id,
        risk_score=risk_score,
        risk_level=risk_level,
        decision=decision,
        explanation=explanation,
        model_version=model_version,
    )
    db.add(assessment)
    db.flush()

    tx.risk_score = risk_score
    tx.risk_level = risk_level
    tx.decision = decision

    for factor in risk_factors:
        event = RiskEvent(
            transaction_id=tx.id,
            event_type=factor.code,
            description=f"{factor.name}: {factor.description}",
            severity=factor.severity,
        )
        db.add(event)

    db.commit()
    db.refresh(assessment)

    if decision in ("REVIEW", "BLOCK") and not _case_exists(db, tx.id):
        _create_case_from_assessment(db, tx, assessment)

    return assessment


def _case_exists(db: Session, transaction_id: int) -> bool:
    from app.models.risk_ops import RiskCase
    return db.query(RiskCase).filter(RiskCase.transaction_id == transaction_id).count() > 0


def _create_case_from_assessment(db: Session, tx: Transaction, assessment: RiskAssessment) -> None:
    from app.models.risk_ops import RiskCase, CaseStatus, CasePriority
    priority = CasePriority.CRITICAL.value if assessment.risk_level == "HIGH" else CasePriority.MEDIUM.value
    case = RiskCase(
        transaction_id=tx.id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        decision=assessment.decision,
        priority=priority,
        status=CaseStatus.OPEN.value,
    )
    db.add(case)
    db.flush()

    log_audit(
        db,
        action=f"AUTO_CASE_CREATED: transaction={tx.id} decision={assessment.decision}",
        entity_type="RISK_CASE",
        entity_id=None,
        details={"transaction_id": tx.id, "risk_score": assessment.risk_score, "risk_level": assessment.risk_level},
    )


def analyze_transaction_result(db: Session, transaction_id: int) -> Optional[Tuple[RiskAssessment, RiskResult]]:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return None

    signals = extract_signals(
        amount=tx.amount,
        currency=tx.currency,
        previous_transaction_amount=tx.previous_transaction_amount,
        transaction_frequency=tx.transaction_frequency,
        failed_attempts=tx.failed_attempts,
        device_change=tx.device_change,
        location_change=tx.location_change,
        merchant_risk=tx.merchant_risk,
        velocity=tx.velocity,
        account_age_days=tx.account_age_days,
        device_id=tx.device_id,
        location=tx.location,
    )

    engine = RulesRiskEngine()
    result = engine.analyze(signals)

    assessment = RiskAssessment(
        transaction_id=tx.id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        decision=result.decision,
        explanation=result.explanation,
        model_version=result.model_version,
    )
    db.add(assessment)
    db.flush()

    tx.risk_score = result.risk_score
    tx.risk_level = result.risk_level
    tx.decision = result.decision

    for factor in result.risk_factors:
        event = RiskEvent(
            transaction_id=tx.id,
            event_type=factor.code,
            description=f"{factor.name}: {factor.description}",
            severity=factor.severity,
        )
        db.add(event)

    db.commit()
    db.refresh(assessment)

    if result.decision in ("REVIEW", "BLOCK") and not _case_exists(db, tx.id):
        _create_case_from_assessment(db, tx, assessment)

    return assessment, result


def get_latest_assessment(db: Session, transaction_id: int) -> Optional[RiskAssessment]:
    return (
        db.query(RiskAssessment)
        .filter(RiskAssessment.transaction_id == transaction_id)
        .order_by(desc(RiskAssessment.created_at))
        .first()
    )


def get_assessment_with_events(db: Session, transaction_id: int) -> Optional[Tuple[RiskAssessment, List[RiskEvent]]]:
    assessment = get_latest_assessment(db, transaction_id)
    if not assessment:
        return None
    events = (
        db.query(RiskEvent)
        .filter(RiskEvent.transaction_id == transaction_id)
        .order_by(desc(RiskEvent.created_at))
        .all()
    )
    return assessment, events


def get_risk_summary(db: Session) -> dict:
    total = db.query(RiskAssessment).count()
    low = db.query(RiskAssessment).filter(RiskAssessment.risk_level == C.RISK_LEVEL_LOW).count()
    medium = db.query(RiskAssessment).filter(RiskAssessment.risk_level == C.RISK_LEVEL_MEDIUM).count()
    high = db.query(RiskAssessment).filter(RiskAssessment.risk_level == C.RISK_LEVEL_HIGH).count()
    allowed = db.query(RiskAssessment).filter(RiskAssessment.decision == C.DECISION_LOW).count()
    review = db.query(RiskAssessment).filter(RiskAssessment.decision == C.DECISION_MEDIUM).count()
    blocked = db.query(RiskAssessment).filter(RiskAssessment.decision == C.DECISION_HIGH).count()

    return {
        "total_assessed": total,
        "low": low,
        "medium": medium,
        "high": high,
        "allowed": allowed,
        "review": review,
        "blocked": blocked,
    }


def get_risk_trends(db: Session, period: str = "7d") -> List[dict]:
    today = date.today()
    if period == "24h":
        days = 1
    elif period == "30d":
        days = 30
    else:
        days = 7

    start_date = datetime.combine(today, datetime.min.time()) - datetime.timedelta(days=days - 1)

    assessments = (
        db.query(RiskAssessment)
        .filter(RiskAssessment.created_at >= start_date)
        .all()
    )

    daily_data = {}
    for a in assessments:
        day_str = a.created_at.strftime("%Y-%m-%d")
        if day_str not in daily_data:
            daily_data[day_str] = {"low": 0, "medium": 0, "high": 0}
        if a.risk_level == C.RISK_LEVEL_LOW:
            daily_data[day_str]["low"] += 1
        elif a.risk_level == C.RISK_LEVEL_MEDIUM:
            daily_data[day_str]["medium"] += 1
        elif a.risk_level == C.RISK_LEVEL_HIGH:
            daily_data[day_str]["high"] += 1

    sorted_dates = sorted(daily_data.keys())
    return [
        {"date": d, "low": daily_data[d]["low"], "medium": daily_data[d]["medium"], "high": daily_data[d]["high"]}
        for d in sorted_dates
    ]


def get_recent_risk_decisions(db: Session, limit: int = 10) -> List[dict]:
    assessments = (
        db.query(RiskAssessment)
        .options(selectinload(RiskAssessment.transaction).selectinload(Transaction.user), selectinload(RiskAssessment.transaction).selectinload(Transaction.merchant))
        .order_by(desc(RiskAssessment.created_at))
        .limit(limit)
        .all()
    )

    results = []
    for a in assessments:
        tx = a.transaction
        results.append({
            "transaction_id": tx.id,
            "transaction_reference": tx.transaction_reference,
            "user_name": tx.user.name if tx.user else None,
            "merchant_name": tx.merchant.name if tx.merchant else None,
            "amount": tx.amount,
            "currency": tx.currency,
            "risk_score": a.risk_score,
            "risk_level": a.risk_level,
            "decision": a.decision,
            "created_at": a.created_at,
        })
    return results


def analyze_transactions_batch(db: Session, transaction_ids: List[int]) -> List[RiskAssessment]:
    assessments = []
    for tx_id in transaction_ids:
        assessment = analyze_transaction(db, tx_id)
        if assessment:
            assessments.append(assessment)
    return assessments


def re_analyze_transaction(db: Session, transaction_id: int) -> Optional[RiskAssessment]:
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return None

    signals = extract_signals(
        amount=tx.amount,
        currency=tx.currency,
        previous_transaction_amount=tx.previous_transaction_amount,
        transaction_frequency=tx.transaction_frequency,
        failed_attempts=tx.failed_attempts,
        device_change=tx.device_change,
        location_change=tx.location_change,
        merchant_risk=tx.merchant_risk,
        velocity=tx.velocity,
        account_age_days=tx.account_age_days,
        device_id=tx.device_id,
        location=tx.location,
    )

    engine = RulesRiskEngine()
    result = engine.analyze(signals)

    assessment = RiskAssessment(
        transaction_id=tx.id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        decision=result.decision,
        explanation=result.explanation,
        model_version=result.model_version,
    )
    db.add(assessment)
    db.flush()

    tx.risk_score = result.risk_score
    tx.risk_level = result.risk_level
    tx.decision = result.decision

    for factor in result.risk_factors:
        event = RiskEvent(
            transaction_id=tx.id,
            event_type=factor.code,
            description=f"{factor.name}: {factor.description}",
            severity=factor.severity,
        )
        db.add(event)

    db.commit()
    db.refresh(assessment)
    return assessment


def analyze_transaction_explainable(db: Session, transaction_id: int):
    import time
    from app.risk.explainable import ExplainableRiskResult, build_explainable_result
    
    overall_start = time.perf_counter()
    
    tx = db.query(Transaction).filter(Transaction.id == transaction_id).first()
    if not tx:
        return None

    signals = extract_signals(
        amount=tx.amount,
        currency=tx.currency,
        previous_transaction_amount=tx.previous_transaction_amount,
        transaction_frequency=tx.transaction_frequency,
        failed_attempts=tx.failed_attempts,
        device_change=tx.device_change,
        location_change=tx.location_change,
        merchant_risk=tx.merchant_risk,
        velocity=tx.velocity,
        account_age_days=tx.account_age_days,
        device_id=tx.device_id,
        location=tx.location,
    )

    rules_engine = RulesRiskEngine()
    rules_result = rules_engine.analyze(signals)

    hybrid_engine = _get_hybrid_engine()
    inference_time_ms = 0.0
    feature_count = 0
    
    if hybrid_engine:
        hybrid_result = hybrid_engine.analyze(
            amount=tx.amount,
            currency=tx.currency,
            previous_transaction_amount=tx.previous_transaction_amount,
            transaction_frequency=tx.transaction_frequency,
            failed_attempts=tx.failed_attempts,
            device_change=tx.device_change,
            location_change=tx.location_change,
            merchant_risk=tx.merchant_risk,
            velocity=tx.velocity,
            account_age_days=tx.account_age_days,
            device_id=tx.device_id,
            location=tx.location,
        )
        inference_time_ms = hybrid_result.inference_time_ms
        feature_count = hybrid_result.feature_count
        
        model = None
        if _ML_AVAILABLE:
            from app.ml.models import get_model
            model = get_model()
        shap_values = explain_transaction(
            model=model,
            amount=tx.amount,
            account_age_days=tx.account_age_days,
            previous_transaction_amount=tx.previous_transaction_amount,
            transaction_frequency=tx.transaction_frequency,
            failed_attempts=tx.failed_attempts,
            device_change=tx.device_change,
            location_change=tx.location_change,
            merchant_risk=tx.merchant_risk,
            velocity=tx.velocity,
            model_version=hybrid_result.model_version,
        )
    else:
        from app.ml.hybrid import HybridRiskResult
        from dataclasses import dataclass
        @dataclass
        class FallbackHybridResult:
            rules_score: int
            rules_level: str
            rules_decision: str
            ml_score: int
            ml_level: str
            ml_decision: str
            ml_probability: float
            final_score: int
            final_level: str
            final_decision: str
            model_version: str
            rules_engine_version: str = "rules-v1"
            inference_time_ms: float = 0.0
            feature_count: int = 0
        hybrid_result = FallbackHybridResult(
            rules_score=rules_result.risk_score,
            rules_level=rules_result.risk_level,
            rules_decision=rules_result.decision,
            ml_score=0,
            ml_level="LOW",
            ml_decision="ALLOW",
            ml_probability=0.0,
            final_score=rules_result.risk_score,
            final_level=rules_result.risk_level,
            final_decision=rules_result.decision,
            model_version="none",
            rules_engine_version="rules-v1",
            inference_time_ms=0.0,
            feature_count=0,
        )
        from app.ml.shap_explainer import SHAPValues
        shap_values = SHAPValues(
            base_value=0.0,
            feature_values={},
            shap_values={},
            feature_contributions=[],
            model_version="none",
            available=False,
        )

    total_time_ms = (time.perf_counter() - overall_start) * 1000
    
    result = build_explainable_result(
        rules_result, 
        hybrid_result, 
        shap_values,
        inference_time_ms=inference_time_ms if inference_time_ms > 0 else total_time_ms,
        feature_count=feature_count if feature_count > 0 else len(signals)
    )
    
    logger.info(
        f"[ML INFERENCE] Transaction: TX-{transaction_id} "
        f"Model: {result.ml_model_version} "
        f"Engine: XGBoost "
        f"Features: {result.feature_count} "
        f"Fraud Probability: {result.ml_probability:.4f} "
        f"Inference Time: {result.inference_time_ms:.2f}ms "
        f"SHAP: {'generated' if result.shap_available else 'unavailable'} "
        f"Hybrid Score: {result.final_score} "
        f"Decision: {result.final_decision}"
    )

    return result


def simulate_transaction_analysis(
    amount: float,
    currency: str,
    payment_method: str,
    merchant_name: str,
    transaction_type: str,
    account_age_days: int,
    transactions_per_hour: int,
    failed_attempts: int,
    device_changed: bool,
    location_changed: bool,
    merchant_risk: float,
):
    import time
    from app.risk.explainable import ExplainableRiskResult, build_explainable_result
    from app.risk.engine import RulesRiskEngine
    from app.risk.feature_extractor import extract_signals

    overall_start = time.perf_counter()

    signals = extract_signals(
        amount=amount,
        currency=currency,
        previous_transaction_amount=amount * 0.8,
        transaction_frequency=transactions_per_hour,
        failed_attempts=failed_attempts,
        device_change=1 if device_changed else 0,
        location_change=1 if location_changed else 0,
        merchant_risk=merchant_risk,
        velocity=transactions_per_hour,
        account_age_days=account_age_days,
        device_id="simulator",
        location="Simulator",
    )

    rules_engine = RulesRiskEngine()
    rules_result = rules_engine.analyze(signals)

    hybrid_engine = _get_hybrid_engine()
    inference_time_ms = 0.0
    feature_count = 0

    if hybrid_engine:
        hybrid_result = hybrid_engine.analyze(
            amount=amount,
            currency=currency,
            previous_transaction_amount=amount * 0.8,
            transaction_frequency=transactions_per_hour,
            failed_attempts=failed_attempts,
            device_change=1 if device_changed else 0,
            location_change=1 if location_changed else 0,
            merchant_risk=merchant_risk,
            velocity=transactions_per_hour,
            account_age_days=account_age_days,
            device_id="simulator",
            location="Simulator",
        )
        inference_time_ms = hybrid_result.inference_time_ms
        feature_count = hybrid_result.feature_count

        model = None
        if _ML_AVAILABLE:
            from app.ml.models import get_model
            model = get_model()
        shap_values = explain_transaction(
            model=model,
            amount=amount,
            account_age_days=account_age_days,
            previous_transaction_amount=amount * 0.8,
            transaction_frequency=transactions_per_hour,
            failed_attempts=failed_attempts,
            device_change=1 if device_changed else 0,
            location_change=1 if location_changed else 0,
            merchant_risk=merchant_risk,
            velocity=transactions_per_hour,
            model_version=hybrid_result.model_version,
        )
    else:
        from app.ml.hybrid import HybridRiskResult
        from dataclasses import dataclass

        @dataclass
        class FallbackHybridResult:
            rules_score: int
            rules_level: str
            rules_decision: str
            ml_score: int
            ml_level: str
            ml_decision: str
            ml_probability: float
            final_score: int
            final_level: str
            final_decision: str
            model_version: str
            rules_engine_version: str = "rules-v1"
            inference_time_ms: float = 0.0
            feature_count: int = 0

        hybrid_result = FallbackHybridResult(
            rules_score=rules_result.risk_score,
            rules_level=rules_result.risk_level,
            rules_decision=rules_result.decision,
            ml_score=0,
            ml_level="LOW",
            ml_decision="ALLOW",
            ml_probability=0.0,
            final_score=rules_result.risk_score,
            final_level=rules_result.risk_level,
            final_decision=rules_result.decision,
            model_version="none",
            rules_engine_version="rules-v1",
            inference_time_ms=0.0,
            feature_count=0,
        )
        from app.ml.shap_explainer import SHAPValues

        shap_values = SHAPValues(
            base_value=0.0,
            feature_values={},
            shap_values={},
            feature_contributions=[],
            model_version="none",
            available=False,
        )

    total_time_ms = (time.perf_counter() - overall_start) * 1000

    result = build_explainable_result(
        rules_result,
        hybrid_result,
        shap_values,
        inference_time_ms=inference_time_ms if inference_time_ms > 0 else total_time_ms,
        feature_count=feature_count if feature_count > 0 else len(signals),
    )

    logger.info(
        f"[SIMULATOR] Amount: {amount} {currency} "
        f"Model: {result.ml_model_version} "
        f"Features: {result.feature_count} "
        f"Fraud Probability: {result.ml_probability:.4f} "
        f"Inference Time: {result.inference_time_ms:.2f}ms "
        f"SHAP: {'generated' if result.shap_available else 'unavailable'} "
        f"Hybrid Score: {result.final_score} "
        f"Decision: {result.final_decision}"
    )

    return result
