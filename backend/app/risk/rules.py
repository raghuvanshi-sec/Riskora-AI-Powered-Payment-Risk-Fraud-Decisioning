from dataclasses import dataclass
from typing import Optional, List
from app.risk import constants as C


@dataclass
class RiskFactor:
    code: str
    name: str
    description: str
    severity: str
    contribution: int


class Rule:
    def __init__(
        self,
        rule_id: str,
        name: str,
        description: str,
        weight: int,
        severity: str,
    ):
        self.rule_id = rule_id
        self.name = name
        self.description = description
        self.weight = weight
        self.severity = severity

    def evaluate(self, signals) -> Optional[RiskFactor]:
        raise NotImplementedError


class UnusualAmountRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="UNUSUAL_AMOUNT",
            name="Unusual Transaction Amount",
            description="Transaction amount is significantly higher than the user's previous transaction.",
            weight=C.WEIGHT_UNUSUAL_AMOUNT,
            severity=C.RULE_SEVERITY_HIGH,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        prev = signals.previous_transaction_amount
        if prev is None or prev <= 0:
            return None
        if signals.amount >= prev * C.UNUSUAL_AMOUNT_MULTIPLIER:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class HighAmountRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="HIGH_AMOUNT",
            name="High Transaction Amount",
            description="Transaction amount exceeds unusually high thresholds for this user segment.",
            weight=C.WEIGHT_HIGH_AMOUNT,
            severity=C.RULE_SEVERITY_CRITICAL,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        if signals.amount > C.AMOUNT_THRESHOLD_MEDIUM:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class NewDeviceRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="NEW_DEVICE",
            name="New Device",
            description="Transaction originated from a newly observed device.",
            weight=C.WEIGHT_NEW_DEVICE,
            severity=C.RULE_SEVERITY_WARNING,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        if signals.device_change is True:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class LocationChangeRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="LOCATION_CHANGE",
            name="Location Change",
            description="Transaction originated from a location that differs from the user's recent activity.",
            weight=C.WEIGHT_LOCATION_CHANGE,
            severity=C.RULE_SEVERITY_WARNING,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        if signals.location_change is True:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class HighVelocityRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="HIGH_VELOCITY",
            name="High Transaction Velocity",
            description="Unusually high frequency of transactions detected within a short time window.",
            weight=C.WEIGHT_HIGH_VELOCITY,
            severity=C.RULE_SEVERITY_CRITICAL,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        vel = signals.velocity
        if vel is not None and vel > C.HIGH_VELOCITY_THRESHOLD:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class FailedAttemptsRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="MULTIPLE_FAILED_ATTEMPTS",
            name="Multiple Failed Attempts",
            description="Multiple failed payment attempts detected before this transaction.",
            weight=C.WEIGHT_FAILED_ATTEMPTS,
            severity=C.RULE_SEVERITY_CRITICAL,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        attempts = signals.failed_attempts
        if attempts is not None and attempts >= C.FAILED_ATTEMPTS_HIGH:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class MerchantRiskRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="HIGH_MERCHANT_RISK",
            name="High Merchant Risk",
            description="Transaction routed through a merchant flagged as elevated risk.",
            weight=C.WEIGHT_MERCHANT_RISK,
            severity=C.RULE_SEVERITY_CRITICAL,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        mr = signals.merchant_risk
        if mr is not None and mr > C.MERCHANT_RISK_HIGH:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


class NewAccountRule(Rule):
    def __init__(self):
        super().__init__(
            rule_id="NEW_ACCOUNT",
            name="New Account",
            description="Transaction from an account created within the last 30 days.",
            weight=C.WEIGHT_NEW_ACCOUNT,
            severity=C.RULE_SEVERITY_INFO,
        )

    def evaluate(self, signals) -> Optional[RiskFactor]:
        age = signals.account_age_days
        if age is not None and age < C.NEW_ACCOUNT_DAYS:
            return RiskFactor(
                code=self.rule_id,
                name=self.name,
                description=self.description,
                severity=self.severity,
                contribution=self.weight,
            )
        return None


ALL_RULES = [
    UnusualAmountRule(),
    HighAmountRule(),
    NewDeviceRule(),
    LocationChangeRule(),
    HighVelocityRule(),
    FailedAttemptsRule(),
    MerchantRiskRule(),
    NewAccountRule(),
]


def get_all_rules() -> List[Rule]:
    return ALL_RULES


def get_rule_by_id(rule_id: str) -> Optional[Rule]:
    for rule in ALL_RULES:
        if rule.rule_id == rule_id:
            return rule
    return None
