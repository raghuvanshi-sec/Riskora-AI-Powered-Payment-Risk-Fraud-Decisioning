from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.api.deps import get_current_active_user, require_risk_analyst
from app.db.database import get_db
from app.models.user import User
from app.schemas.risk_api import (
    RiskAnalysisResponse,
    RiskDecisionItem,
    RiskEventResponse,
    RiskFactorResponse,
    RiskSummaryResponse,
    RiskTrendItem,
    ExplainableAnalysisResponse,
    SHAPFactorResponse,
)
from app.services import risk_service
from app.services.audit_service import log_audit

router = APIRouter()


@router.post(
    "/risk/analyze/{transaction_id}",
    response_model=RiskAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["risk"],
)
def analyze_transaction(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
):
    assessment, result = risk_service.analyze_transaction_result(db, transaction_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    log_audit(
        db,
        action="RISK_ANALYSIS_RUN",
        entity_type="TRANSACTION",
        entity_id=str(transaction_id),
        user_id=current_user.id,
        details={"risk_score": assessment.risk_score, "risk_level": assessment.risk_level},
    )
    db.commit()

    return RiskAnalysisResponse(
        transaction_id=transaction_id,
        risk_score=result.risk_score,
        risk_level=result.risk_level,
        decision=result.decision,
        explanation=result.explanation,
        model_version=result.model_version,
        risk_factors=[
            RiskFactorResponse(
                code=f.code,
                name=f.name,
                description=f.description,
                severity=f.severity,
                contribution=f.contribution,
            )
            for f in result.risk_factors
        ],
    )


@router.get(
    "/risk/transactions/{transaction_id}",
    response_model=RiskAnalysisResponse,
    tags=["risk"],
)
def get_transaction_risk(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    assessment, events = risk_service.get_assessment_with_events(db, transaction_id)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk assessment found for this transaction",
        )

    risk_factors = []
    for ev in events:
        parts = ev.description.split(": ", 1) if ev.description else [ev.event_type, ""]
        risk_factors.append(RiskFactorResponse(
            code=ev.event_type,
            name=parts[0] if parts else ev.event_type,
            description=parts[1] if len(parts) > 1 else "",
            severity=ev.severity,
            contribution=0,
        ))

    return RiskAnalysisResponse(
        transaction_id=transaction_id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        decision=assessment.decision,
        explanation=assessment.explanation,
        model_version=assessment.model_version,
        risk_factors=risk_factors,
    )


@router.get(
    "/risk/summary",
    response_model=RiskSummaryResponse,
    tags=["risk"],
)
def get_risk_summary(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    return risk_service.get_risk_summary(db)


@router.get(
    "/risk/trends",
    response_model=List[RiskTrendItem],
    tags=["risk"],
)
def get_risk_trends(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    period: str = Query("7d", pattern="^(24h|7d|30d)$"),
):
    return risk_service.get_risk_trends(db, period=period)


@router.get(
    "/risk/recent",
    response_model=List[RiskDecisionItem],
    tags=["risk"],
)
def get_recent_risk_decisions(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
):
    return risk_service.get_recent_risk_decisions(db, limit=limit)


@router.get(
    "/risk/events",
    response_model=List[RiskEventResponse],
    tags=["risk"],
)
def get_risk_events(
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    transaction_id: Optional[int] = Query(None),
    severity: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
):
    from app.models.risk import RiskEvent
    from sqlalchemy import desc

    q = db.query(RiskEvent)
    if transaction_id is not None:
        q = q.filter(RiskEvent.transaction_id == transaction_id)
    if severity is not None:
        q = q.filter(RiskEvent.severity == severity)

    events = q.order_by(desc(RiskEvent.created_at)).limit(limit).all()
    return events


@router.get(
    "/risk/models",
    tags=["risk"],
)
def list_models(
    current_user: User = Depends(get_current_active_user),
):
    from app.services import ml_service
    return {
        "available": ml_service.is_ml_available(),
        "versions": ml_service.list_model_versions(),
    }


@router.get(
    "/risk/models/{version}",
    tags=["risk"],
)
def get_model_info(
    version: str,
    current_user: User = Depends(get_current_active_user),
):
    from app.services import ml_service
    info = ml_service.get_model_info(version)
    if not info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return info


@router.post(
    "/risk/models/{version}/activate",
    status_code=status.HTTP_200_OK,
    tags=["risk"],
)
def activate_model(
    version: str,
    current_user: User = Depends(require_risk_analyst),
):
    from app.services import ml_service
    success = ml_service.set_active_model(version)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Model version not found",
        )
    return {"message": f"Model {version} activated", "version": version}


@router.post(
    "/risk/analyze/{transaction_id}/ml",
    response_model=RiskAnalysisResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["risk"],
)
def analyze_transaction_ml(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_risk_analyst),
):
    assessment = risk_service.analyze_transaction(db, transaction_id, use_ml=True)
    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    log_audit(
        db,
        action="RISK_ANALYSIS_RUN",
        entity_type="TRANSACTION",
        entity_id=str(transaction_id),
        user_id=current_user.id,
        details={"risk_score": assessment.risk_score, "risk_level": assessment.risk_level, "engine": "hybrid"},
    )
    db.commit()

    events = db.query(RiskEvent).filter(RiskEvent.transaction_id == transaction_id).order_by(desc(RiskEvent.created_at)).all()
    risk_factors = []
    for ev in events:
        parts = ev.description.split(": ", 1) if ev.description else [ev.event_type, ""]
        risk_factors.append(RiskFactorResponse(
            code=ev.event_type,
            name=parts[0] if parts else ev.event_type,
            description=parts[1] if len(parts) > 1 else "",
            severity=ev.severity,
            contribution=0,
        ))

    return RiskAnalysisResponse(
        transaction_id=transaction_id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        decision=assessment.decision,
        explanation=assessment.explanation or "",
        model_version=assessment.model_version or "unknown",
        risk_factors=risk_factors,
    )


@router.get(
    "/risk/analyze/{transaction_id}/explain",
    response_model=ExplainableAnalysisResponse,
    tags=["risk"],
)
def explain_transaction(
    transaction_id: int,
    *,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    result = risk_service.analyze_transaction_explainable(db, transaction_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    rules_factors = [
        RiskFactorResponse(
            code=f.code,
            name=f.name,
            description=f.description,
            severity=f.severity,
            contribution=f.contribution,
        )
        for f in result.rules_factors
    ]
    shap_factors = [
        SHAPFactorResponse(
            feature_name=f.feature_name,
            feature_value=f.feature_value,
            contribution=f.contribution,
            direction=f.direction,
        )
        for f in result.shap_factors
    ]

    return ExplainableAnalysisResponse(
        transaction_id=transaction_id,
        final_score=result.final_score,
        final_level=result.final_level,
        final_decision=result.final_decision,
        rules_score=result.rules_score,
        rules_level=result.rules_level,
        rules_decision=result.rules_decision,
        ml_score=result.ml_score,
        ml_level=result.ml_level,
        ml_decision=result.ml_decision,
        ml_probability=result.ml_probability,
        rules_factors=rules_factors,
        shap_factors=shap_factors,
        explanation=result.explanation,
        rules_engine_version=result.rules_engine_version,
        ml_model_version=result.ml_model_version,
        shap_available=result.shap_available,
    )
