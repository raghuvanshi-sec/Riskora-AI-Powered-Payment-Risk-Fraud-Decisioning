"""
IEEE-CIS Risk Assessment Routes
==============================

API routes for IEEE-CIS fraud risk assessment.
"""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_active_user
from app.db.database import get_db
from app.models.user import User
from app.schemas.ieee_risk import (
    IEEETransactionInput,
    IEEERiskAssessmentResponse,
    IEEERiskHealthResponse,
    IEEERiskAssessmentDBResponse,
    IEEERiskAssessmentFullResponse,
    IEEERiskHistoryResponse,
    IEEERiskHistoryItem,
    IEEERiskEventsResponse,
    IEEERiskEventResponse,
    TriggeredRule,
    SHAPFeature,
)
from app.services.ieee_risk_service import get_ieee_risk_service
from app.services import risk_persistence_service


router = APIRouter(prefix="/risk", tags=["ieee-risk"])


@router.post(
    "/assess",
    response_model=IEEERiskAssessmentResponse,
    summary="Assess transaction risk",
    description="Evaluate a transaction for fraud risk using the IEEE-CIS hybrid model.",
    responses={
        200: {"description": "Risk assessment completed"},
        201: {"description": "Risk assessment persisted"},
        500: {"description": "Risk service unavailable"},
    },
)
async def assess_risk(
    transaction: IEEETransactionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    transaction_id: int = Query(None, description="Optional transaction ID to persist assessment"),
    persist: bool = Query(True, description="Whether to persist the assessment"),
) -> IEEERiskAssessmentResponse:
    """
    Perform risk assessment on a transaction.

    If transaction_id is provided and persist=True, the assessment will be
    stored in the database along with triggered rules, SHAP features,
    and a risk event.

    If transaction_id is not provided, performs inference only without persistence.
    """
    try:
        service = get_ieee_risk_service()

        if service.model is None:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Risk model not loaded",
            )

        result = service.assess(transaction.model_dump())

        if transaction_id is not None and persist:
            try:
                assessment, triggered_rules, shap_features = risk_persistence_service.create_risk_assessment(
                    db,
                    transaction_id=transaction_id,
                    inference_result=result,
                    user_id=current_user.id,
                )

                risk_persistence_service.create_risk_event(
                    db,
                    transaction_id=transaction_id,
                    event_type="RISK_ASSESSED",
                    description=f"Risk assessment performed: {result['risk_level']} / {result['decision']}",
                    severity=_severity_from_level(result["risk_level"]),
                    user_id=current_user.id,
                )

                db.commit()

            except ValueError as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=str(e),
                )
            except Exception as e:
                db.rollback()
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to persist assessment: {str(e)}",
                )

        return IEEERiskAssessmentResponse(**result)

    except HTTPException:
        raise
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Model artifact not found: {e}",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Risk assessment failed: {str(e)}",
        )


@router.get(
    "/transactions/{transaction_id}",
    response_model=IEEERiskAssessmentFullResponse,
    summary="Get latest risk assessment for transaction",
    description="Retrieve the most recent persisted risk assessment for a transaction.",
    responses={
        200: {"description": "Risk assessment retrieved"},
        404: {"description": "No assessment found"},
    },
)
async def get_latest_assessment(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> IEEERiskAssessmentFullResponse:
    """
    Get the latest risk assessment for a transaction.

    Returns the most recent assessment with all triggered rules
    and SHAP feature contributions.
    """
    assessment = risk_persistence_service.get_latest_risk_assessment(db, transaction_id)

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No risk assessment found for transaction {transaction_id}",
        )

    triggered_rules = [
        TriggeredRule(
            rule_id=r.rule_id,
            name=r.name,
            severity=r.severity,
            score_contribution=r.score_contribution,
            triggered=r.triggered,
            reason=r.reason or "",
        )
        for r in assessment.triggered_rules
    ]

    rule_reasons = [r.reason for r in triggered_rules if r.triggered and r.reason]

    positive_features = []
    negative_features = []

    for feat in assessment.shap_features:
        shap_feat = SHAPFeature(
            feature_name=feat.feature_name,
            shap_value=feat.shap_value,
            direction=feat.direction,
        )
        if feat.direction == "increases_risk":
            positive_features.append(shap_feat)
        else:
            negative_features.append(shap_feat)

    return IEEERiskAssessmentFullResponse(
        id=assessment.id,
        transaction_id=assessment.transaction_id,
        risk_score=assessment.risk_score,
        risk_level=assessment.risk_level,
        decision=assessment.decision,
        explanation=assessment.explanation,
        model_version=assessment.model_version,
        preprocessor_version=assessment.preprocessor_version,
        ml_probability=assessment.ml_probability,
        ml_score=assessment.ml_score,
        rule_score=assessment.rule_score,
        triggered_rules=triggered_rules,
        rule_reasons=rule_reasons,
        top_positive_features=positive_features,
        top_negative_features=negative_features,
        created_at=assessment.created_at,
    )


@router.get(
    "/transactions/{transaction_id}/history",
    response_model=IEEERiskHistoryResponse,
    summary="Get risk assessment history for transaction",
    description="Retrieve historical risk assessments for a transaction, newest first.",
    responses={
        200: {"description": "Risk history retrieved"},
    },
)
async def get_risk_history(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    limit: int = Query(10, ge=1, le=50),
) -> IEEERiskHistoryResponse:
    """
    Get historical risk assessments for a transaction.

    Returns assessments ordered by creation time, newest first.
    """
    assessments = risk_persistence_service.get_risk_history(db, transaction_id, limit=limit)

    history_items = [
        IEEERiskHistoryItem(
            id=a.id,
            risk_score=a.risk_score,
            risk_level=a.risk_level,
            decision=a.decision,
            ml_probability=a.ml_probability,
            ml_score=a.ml_score,
            rule_score=a.rule_score,
            created_at=a.created_at,
        )
        for a in assessments
    ]

    return IEEERiskHistoryResponse(
        transaction_id=transaction_id,
        assessments=history_items,
        total=len(history_items),
    )


@router.get(
    "/transactions/{transaction_id}/events",
    response_model=IEEERiskEventsResponse,
    summary="Get risk events for transaction",
    description="Retrieve risk events for a transaction.",
    responses={
        200: {"description": "Risk events retrieved"},
    },
)
async def get_risk_events(
    transaction_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
    event_type: str = Query(None, description="Filter by event type"),
    limit: int = Query(50, ge=1, le=100),
) -> IEEERiskEventsResponse:
    """
    Get risk events for a transaction.

    Returns events ordered by creation time, newest first.
    """
    events = risk_persistence_service.get_risk_events(
        db, transaction_id, limit=limit, event_type=event_type
    )

    event_responses = [
        IEEERiskEventResponse(
            id=e.id,
            transaction_id=e.transaction_id,
            event_type=e.event_type,
            description=e.description,
            severity=e.severity,
            created_at=e.created_at,
        )
        for e in events
    ]

    return IEEERiskEventsResponse(
        transaction_id=transaction_id,
        events=event_responses,
        total=len(event_responses),
    )


@router.get(
    "/health",
    response_model=IEEERiskHealthResponse,
    summary="Risk engine health check",
    description="Check the health status of the IEEE-CIS risk engine.",
    responses={
        200: {"description": "Health status retrieved"},
        503: {"description": "Risk service unavailable"},
    },
)
async def health_check() -> IEEERiskHealthResponse:
    """
    Check the health of the IEEE-CIS risk engine.

    Returns whether the model and preprocessor are loaded,
    along with their versions.
    """
    try:
        service = get_ieee_risk_service()
        health = service.health_check()

        if health["model_loaded"]:
            return IEEERiskHealthResponse(**health)
        else:
            return JSONResponse(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                content=health,
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={
                "status": "error",
                "model_loaded": False,
                "preprocessor_loaded": False,
                "detail": str(e),
            },
        )


def _severity_from_level(risk_level: str) -> str:
    """Map risk level to event severity."""
    mapping = {
        "HIGH": "CRITICAL",
        "MEDIUM": "WARNING",
        "LOW": "INFO",
    }
    return mapping.get(risk_level, "INFO")
