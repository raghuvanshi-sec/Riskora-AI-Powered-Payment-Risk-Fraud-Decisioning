from fastapi import APIRouter
from app.api.routes import auth, transactions, risk_ops, ieee_risk, risk

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(transactions.router, tags=["transactions"])
api_router.include_router(risk_ops.router, tags=["risk-ops"])
api_router.include_router(ieee_risk.router, tags=["ieee-risk"])
api_router.include_router(risk.router, tags=["risk"])
