from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field

from app.risk.engine import RiskResult as RulesRiskResult
from app.risk.rules import RiskFactor
from app.ml.hybrid import HybridRiskResult
from app.ml.shap_explainer import SHAPValues, FeatureContribution


@dataclass
class RuleFactorExplanation:
    code: str
    name: str
    description: str
    severity: str
    contribution: int


@dataclass
class SHAPFactorExplanation:
    feature_name: str
    feature_value: float
    contribution: float
    direction: str


@dataclass
class ExplainableRiskResult:
    final_score: int
    final_level: str
    final_decision: str
    rules_score: int
    rules_level: str
    rules_decision: str
    ml_score: int
    ml_level: str
    ml_decision: str
    ml_probability: float
    rules_factors: List[RuleFactorExplanation]
    shap_factors: List[SHAPFactorExplanation]
    explanation: str
    rules_engine_version: str
    ml_model_version: str
    shap_available: bool
    inference_time_ms: float = 0.0
    feature_count: int = 0


def rule_factors_to_explanation(factors: List[RiskFactor]) -> List[RuleFactorExplanation]:
    return [
        RuleFactorExplanation(
            code=f.code,
            name=f.name,
            description=f.description,
            severity=f.severity,
            contribution=f.contribution,
        )
        for f in factors
    ]


def shap_to_explanation(shap_values: SHAPValues) -> List[SHAPFactorExplanation]:
    if not shap_values.available:
        return []
    return [
        SHAPFactorExplanation(
            feature_name=fc.feature_name,
            feature_value=fc.feature_value,
            contribution=fc.contribution,
            direction=fc.direction,
        )
        for fc in shap_values.feature_contributions[:10]
    ]


def generate_explanation(
    rules_factors: List[RuleFactorExplanation],
    shap_factors: List[SHAPFactorExplanation],
    final_level: str,
    final_decision: str,
    shap_available: bool,
) -> str:
    parts = []

    if rules_factors:
        factor_names = [f.name for f in rules_factors]
        if len(factor_names) == 1:
            parts.append(f"{factor_names[0]} was detected")
        elif len(factor_names) == 2:
            parts.append(f"{factor_names[0]} and {factor_names[1]} were detected")
        else:
            parts.append(f"Multiple risk factors were detected: {', '.join(factor_names)}")

    if shap_available and shap_factors:
        top_shap = shap_factors[:3]
        shap_descriptions = []
        for f in top_shap:
            if abs(f.contribution) > 0.01:
                direction = "significantly higher" if f.contribution > 0 else "significantly lower"
                shap_descriptions.append(f"{f.feature_name} ({direction} than expected)")
        if shap_descriptions:
            parts.append(f"ML model analysis shows: {'; '.join(shap_descriptions)}")

    if not parts:
        return f"Transaction classified as {final_level} risk. Decision: {final_decision}."

    explanation = ". ".join(parts)
    explanation += f". Overall classification: {final_level} risk. Decision: {final_decision}."

    return explanation


def build_explainable_result(
    rules_result: RulesRiskResult,
    hybrid_result: HybridRiskResult,
    shap_values: SHAPValues,
    inference_time_ms: float = 0.0,
    feature_count: int = 0,
) -> ExplainableRiskResult:
    rules_factors = rule_factors_to_explanation(rules_result.risk_factors)
    shap_factors = shap_to_explanation(shap_values)

    explanation = generate_explanation(
        rules_factors=rules_factors,
        shap_factors=shap_factors,
        final_level=hybrid_result.final_level,
        final_decision=hybrid_result.final_decision,
        shap_available=shap_values.available,
    )

    return ExplainableRiskResult(
        final_score=hybrid_result.final_score,
        final_level=hybrid_result.final_level,
        final_decision=hybrid_result.final_decision,
        rules_score=hybrid_result.rules_score,
        rules_level=hybrid_result.rules_level,
        rules_decision=hybrid_result.rules_decision,
        ml_score=hybrid_result.ml_score,
        ml_level=hybrid_result.ml_level,
        ml_decision=hybrid_result.ml_decision,
        ml_probability=hybrid_result.ml_probability,
        rules_factors=rules_factors,
        shap_factors=shap_factors,
        explanation=explanation,
        rules_engine_version=hybrid_result.rules_engine_version,
        ml_model_version=hybrid_result.model_version,
        shap_available=shap_values.available,
        inference_time_ms=inference_time_ms,
        feature_count=feature_count,
    )
