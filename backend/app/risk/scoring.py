from typing import List
from app.risk import constants as C
from app.risk.rules import RiskFactor


def calculate_score(risk_factors: List[RiskFactor]) -> int:
    score = sum(f.contribution for f in risk_factors)
    return max(C.MIN_SCORE, min(C.MAX_SCORE, score))


def get_risk_level(score: int) -> str:
    if score >= C.HIGH_THRESHOLD:
        return C.RISK_LEVEL_HIGH
    if score >= C.LOW_THRESHOLD:
        return C.RISK_LEVEL_MEDIUM
    return C.RISK_LEVEL_LOW


def get_decision(risk_level: str) -> str:
    if risk_level == C.RISK_LEVEL_HIGH:
        return C.DECISION_HIGH
    if risk_level == C.RISK_LEVEL_MEDIUM:
        return C.DECISION_MEDIUM
    return C.DECISION_LOW


def generate_explanation(risk_factors: List[RiskFactor], risk_level: str) -> str:
    if not risk_factors:
        return "No risk factors detected. Transaction appears normal."

    factor_names = [f.name for f in risk_factors]
    if len(factor_names) == 1:
        explanation = f"This transaction was flagged because {factor_names[0].lower()} was detected."
    elif len(factor_names) == 2:
        explanation = f"This transaction was flagged because {factor_names[0].lower()} and {factor_names[1].lower()} were detected."
    else:
        explanation = f"This transaction was flagged because the following risk factors were detected: {', '.join(f.name.lower() for f in risk_factors)}."

    risk_level_descriptions = {
        C.RISK_LEVEL_HIGH: "classified as high risk",
        C.RISK_LEVEL_MEDIUM: "classified as medium risk",
        C.RISK_LEVEL_LOW: "classified as low risk",
    }

    level_desc = risk_level_descriptions.get(risk_level, "classified with uncertain risk")
    explanation += f" The transaction is {level_desc}."

    return explanation
