# Product Requirements Document (PRD)
## AI Risk Manager — Razorpay Track

**Product Type:** AI-powered payment risk and fraud decisioning platform  
**Target Users:** Merchants, payment/risk teams, fraud analysts, operations teams  
**Version:** MVP / Version 1.0  
**Product Stage:** Early-stage prototype  
**Primary Objective:** Detect and assess risky payment activity in real time and help businesses make faster, safer transaction decisions.

---

# 1. Executive Summary

AI Risk Manager is an AI-powered payment risk management platform designed to help merchants identify potentially fraudulent, suspicious, or high-risk transactions before financial loss occurs.

The system analyzes transaction attributes and behavioral signals, calculates a **risk score**, explains the factors contributing to that score, and recommends an appropriate action such as:

- **Approve**
- **Review**
- **Block**

Instead of relying only on static fraud rules, the platform combines **machine learning, transaction intelligence, rule-based checks, and explainable risk scoring** to create a more adaptive risk-management layer.

The core product philosophy is:

> **Don't just tell the merchant that a transaction is risky. Tell them why it is risky and what they should do about it.**

The MVP will focus on transaction-level risk assessment, explainability, a merchant dashboard, alerts, and basic risk analytics.

---

# 2. Problem Statement

Digital payments are fast, but fraud can be faster.

Merchants can face:

- Stolen-card transactions
- Account takeover
- Unusual transaction behavior
- High-frequency transaction attacks
- Suspicious IP/device activity
- Multiple transactions from the same account
- Abnormally large transactions
- Card testing attacks
- New-account abuse
- Repeated failed payment attempts
- Coordinated fraudulent activity

Traditional rule-based systems have several limitations.

### Problem 1 — Static Rules

Rules such as:

> "Block transactions above ₹50,000."

can stop some fraud but may also block legitimate customers.

### Problem 2 — Too Many Signals

A transaction may look normal individually but become suspicious when combined with behavioral information.

For example:

> A customer normally spends ₹1,000–₹3,000 in India.

Then suddenly:

> ₹75,000 transaction + new device + foreign IP + five failed attempts.

The combination is significantly more suspicious than any individual signal.

### Problem 3 — Lack of Explainability

A simple:

> "Transaction blocked."

is not enough for a merchant or fraud analyst.

They need to know:

- Why was it flagged?
- Which signals increased the risk?
- How severe is the risk?
- What action should be taken?

### Problem 4 — Operational Overload

Fraud teams cannot manually investigate every transaction.

The platform therefore needs to prioritize:

**High-risk transactions → human review**

while allowing:

**Low-risk transactions → automatic approval**

---

# 3. Product Vision

Build an intelligent risk layer that continuously evaluates payment activity and converts complex transaction data into a simple business decision.

### Vision

> **Make every payment decision faster, safer, and explainable.**

The long-term vision is to evolve from a transaction fraud detector into an intelligent **payment risk operating system** capable of detecting fraud patterns, merchant risk, account abuse, and emerging threats.

---

# 4. Target Users

## Primary User — Merchant

Businesses accepting online payments.

### Needs

- Reduce fraud losses
- Reduce chargebacks
- Avoid blocking legitimate customers
- Understand suspicious transactions
- Monitor risk trends
- Configure risk thresholds

---

## Secondary User — Fraud Analyst

A person responsible for investigating suspicious transactions.

### Needs

- Investigation queue
- Transaction history
- Risk explanations
- Supporting evidence
- Ability to approve/block/review
- Identify recurring fraud patterns

---

## Secondary User — Risk Operations Manager

Responsible for overall payment risk.

### Needs

- Fraud rate
- Risk distribution
- Block/review/approve rates
- Emerging patterns
- Model performance
- Merchant-level risk trends

---

# 5. Product Goals

## Primary Goals

1. Detect suspicious transactions in real time.
2. Generate a transaction-level risk score.
3. Provide explainable reasons for the score.
4. Recommend an action.
5. Give merchants a centralized risk dashboard.
6. Reduce manual investigation effort.
7. Detect behavioral anomalies rather than relying exclusively on static rules.

## Secondary Goals

- Provide historical risk analytics.
- Allow merchants to configure basic risk thresholds.
- Generate alerts for unusual activity.
- Create an investigation workflow.
- Continuously improve risk detection using feedback.

---

# 6. Non-Goals

The first version will deliberately avoid becoming an enormous enterprise fraud platform.

We are **NOT** building:

- A complete payment gateway
- A banking core system
- A replacement for payment processing infrastructure
- A fully autonomous fraud investigation system
- A global identity verification/KYC platform
- A chargeback management platform
- A cryptocurrency fraud platform
- A customer-facing banking application
- A perfect fraud prediction system
- A fully autonomous model retraining pipeline
- A complex graph database in V1
- A mobile application in V1

The MVP should demonstrate **risk intelligence**, not attempt to rebuild the entire payments ecosystem.

---

# 7. Core Product Workflow

The fundamental workflow is:

**Transaction → Feature Extraction → Rule Checks → ML Risk Model → Risk Score → Explanation → Decision → Dashboard/Alert → Analyst Feedback**

Example:

### Transaction

Amount: ₹48,000  
Country: India  
Device: New  
IP: Unknown  
Previous failed attempts: 4  
Account age: 2 days

### AI Analysis

The system evaluates:

- Transaction amount
- Transaction frequency
- Device history
- IP reputation
- Account age
- Failed attempts
- Geographic deviation
- Historical behavior

### Risk Score

**87 / 100 — HIGH RISK**

### Explanation

Top contributing factors:

1. Unusually high transaction amount
2. New device
3. Multiple failed attempts
4. Newly created account
5. Abnormal transaction velocity

### Recommendation

**BLOCK**

This is the central product experience.

---

# 8. Risk Score

Every transaction receives a normalized risk score:

**0–100**

| Score | Risk Level | Recommended Action |
|---|---|---|
| 0–30 | Low | Approve |
| 31–70 | Medium | Review |
| 71–100 | High | Block / Manual Review |

These thresholds should remain configurable.

The score should not be presented as absolute truth.

Instead:

> **Risk Score: 87 — High Risk**

with an explanation of the evidence behind the score.

---

# 9. Core Features

## Feature 1 — Real-Time Transaction Risk Scoring

### Priority: MUST HAVE

The system receives transaction information and evaluates its risk.

### Input examples

- Transaction ID
- Amount
- Currency
- Timestamp
- Customer/account ID
- Payment method
- Device information
- IP information
- Location
- Transaction history
- Failed attempts

### Output

- Risk score
- Risk category
- Recommended action
- Risk reasons

---

# 10. Feature 2 — AI/ML Fraud Detection

### Priority: MUST HAVE

A machine-learning model evaluates transaction patterns and estimates the probability that a transaction is suspicious.

Possible MVP models:

- Logistic Regression
- Random Forest
- XGBoost

For an initial prototype, **XGBoost** is a strong candidate because it handles structured/tabular transaction data effectively.

The model should output a probability that can be transformed into the product's risk score.

---

# 11. Feature 3 — Rule-Based Risk Engine

### Priority: MUST HAVE

ML should not be the only decision mechanism.

The platform should also support deterministic rules.

Examples:

```text
IF amount > customer's normal transaction range
THEN increase risk

IF failed_attempts > threshold
THEN increase risk

IF new_device = true AND high_amount = true
THEN increase risk

IF transaction_velocity > threshold
THEN increase risk
```

This creates a hybrid:

**Rules + ML = Risk Decision**

This is preferable to relying entirely on a black-box model.

---

# 12. Feature 4 — Explainable AI

### Priority: MUST HAVE

The platform must explain why a transaction received its risk score.

Example:

**Risk Score: 82**

### Top Risk Factors

- 🔴 Transaction amount is 4.2× normal
- 🔴 New device detected
- 🔴 5 failed attempts in the last 10 minutes
- 🟠 Account created recently
- 🟠 Unusual transaction velocity

The explanation should be understandable to a business user rather than only a data scientist.

---

# 13. Feature 5 — Risk Dashboard

### Priority: MUST HAVE

The dashboard provides an overview of payment risk.

### Key KPIs

- Total transactions
- High-risk transactions
- Blocked transactions
- Transactions requiring review
- Fraud rate
- Average risk score
- Estimated prevented loss
- Risk trend

Example:

```text
Today's Risk Overview

Transactions          24,892
High Risk                427
Blocked                  183
Manual Review            244
Average Risk Score       24
Estimated Loss Prevented ₹3.8L
```

---

# 14. Feature 6 — Transaction Investigation

### Priority: MUST HAVE

Analysts should be able to open a transaction and inspect its risk profile.

### Transaction Details

- Transaction ID
- Amount
- Customer
- Timestamp
- Device
- IP
- Location
- Risk score
- Risk level
- Model probability
- Triggered rules
- Risk factors
- Previous transactions
- Recommended action

The analyst should be able to:

**Approve / Block / Mark for Review**

---

# 15. Feature 7 — Risk Alerts

### Priority: MUST HAVE

The system should alert users when unusual activity occurs.

Examples:

> 🚨 High-risk transaction detected.

> 🚨 27 transactions from the same device in 5 minutes.

> 🚨 Unusual transaction spike detected.

> 🚨 Fraud risk increased by 34% compared with the previous period.

For the MVP, dashboard notifications are sufficient.

Email/SMS/WhatsApp notifications can come later.

---

# 16. Feature 8 — Risk Rules Configuration

### Priority: NICE TO HAVE

Allow merchants to configure basic rules.

Example:

```text
Transaction Amount > ₹50,000
→ Review

More than 5 failed attempts
→ High Risk

New Device + Amount > ₹20,000
→ Review
```

This provides merchants with control over the risk engine.

---

# 17. Feature 9 — Historical Analytics

### Priority: NICE TO HAVE

Provide historical trends.

Metrics:

- Fraud rate by day
- Risk score distribution
- Block rate
- Review rate
- Transaction volume
- High-risk transaction trends
- Risk by payment method

---

# 18. Feature 10 — Feedback Loop

### Priority: NICE TO HAVE

When an analyst changes a system decision:

```text
AI → BLOCK
Analyst → APPROVE
```

that decision can become feedback for future model improvement.

Similarly:

```text
AI → APPROVE
Actual fraud discovered later
```

can become a negative training signal.

This enables the product to gradually become more adaptive.

---

# 19. Feature Prioritization

## MUST HAVE — MVP

- Transaction ingestion
- Feature extraction
- ML risk scoring
- Rule-based risk engine
- Risk score
- Risk categories
- Explainable risk factors
- Approve/Review/Block recommendation
- Risk dashboard
- Transaction investigation
- Basic alerts
- Transaction history

## NICE TO HAVE — V1.1+

- Custom merchant rules
- Advanced analytics
- Analyst feedback loop
- Model performance dashboard
- Device fingerprint intelligence
- IP reputation integration
- Automated anomaly detection
- Risk heatmaps
- Customer behavioral profiles

## FUTURE

- Graph-based fraud detection
- Account takeover detection
- Cross-merchant intelligence
- Adaptive real-time model retraining
- Network-level fraud detection
- Advanced behavioral biometrics
- Automated fraud investigation agent
- Predictive chargeback prevention

---

# 20. User Journey

## Step 1 — Merchant Login

Merchant enters the platform.

↓

## Step 2 — Dashboard

Merchant sees:

- Transaction volume
- Current risk level
- High-risk transactions
- Alerts
- Risk trends

↓

## Step 3 — Transaction Arrives

A new transaction enters the system.

↓

## Step 4 — Risk Engine

The system extracts relevant features.

↓

## Step 5 — AI Analysis

ML model evaluates the transaction.

↓

## Step 6 — Rule Evaluation

Risk rules are checked.

↓

## Step 7 — Risk Score

System generates:

**Risk Score = 82**

↓

## Step 8 — Explainability

System shows:

> High transaction amount  
> New device  
> Unusual velocity  
> Multiple failed attempts

↓

## Step 9 — Decision

System recommends:

**BLOCK**

↓

## Step 10 — Analyst Review

For review-level transactions, the analyst investigates.

↓

## Step 11 — Final Decision

Analyst:

**Approve / Block**

↓

## Step 12 — Feedback

Decision is stored for analytics and future model improvement.

---

# 21. MVP Definition

The MVP should answer one fundamental question:

> **Can our system identify risky payment transactions and provide an understandable reason for its decision?**

The MVP therefore consists of five major components.

### 1. Transaction Engine

Accept transaction data through an API.

### 2. Risk Engine

Combine:

**ML Model + Rules**

### 3. Explainability Layer

Convert model/rule outputs into human-readable risk reasons.

### 4. Merchant Dashboard

Display:

- Transactions
- Risk scores
- Risk categories
- Alerts
- Analytics

### 5. Investigation Interface

Allow an analyst to inspect and act on suspicious transactions.

---

# 22. Suggested MVP Architecture

```text
                    PAYMENT TRANSACTION
                            │
                            ▼
                     API / Ingestion
                            │
                            ▼
                   Feature Extraction
                            │
                ┌───────────┴───────────┐
                ▼                       ▼
         Rule Engine               ML Model
                │                       │
                └───────────┬───────────┘
                            ▼
                     Risk Aggregator
                            │
                            ▼
                     Risk Score 0–100
                            │
                ┌───────────┼───────────┐
                ▼           ▼           ▼
             APPROVE      REVIEW      BLOCK
                            │
                            ▼
                   Explainability Layer
                            │
                            ▼
                    Merchant Dashboard
                            │
                            ▼
                     Analyst Feedback
```

---

# 23. Data Requirements

The MVP dataset should contain transaction-level features.

### Transaction Features

- Transaction amount
- Transaction frequency
- Transaction timestamp
- Payment method
- Transaction status

### Customer Features

- Account age
- Previous transaction count
- Average transaction amount
- Historical failure rate

### Device Features

- Device ID
- New device indicator
- Number of accounts using device

### Network Features

- IP address
- Country
- Location
- IP risk/reputation indicator

### Behavioral Features

- Transactions in last 5 minutes
- Transactions in last hour
- Average spending deviation
- Failed attempts
- Time since previous transaction

### Target

```text
fraud = 0
fraud = 1
```

---

# 24. Technical Product Requirements

## Frontend

Recommended:

- React
- JavaScript
- CSS
- Charting library

The interface should prioritize a clean fintech dashboard rather than a flashy consumer UI.

---

## Backend

Recommended:

- Python
- FastAPI

Responsibilities:

- Transaction API
- Risk scoring
- Rule evaluation
- Authentication
- Dashboard APIs
- Alert generation

---

## ML

Recommended:

- Pandas
- NumPy
- Scikit-learn
- XGBoost

Model pipeline:

```text
Raw Data
   ↓
Cleaning
   ↓
Feature Engineering
   ↓
Train/Test Split
   ↓
Model Training
   ↓
Evaluation
   ↓
Risk Probability
   ↓
Risk Score
```

---

## Database

Recommended:

**PostgreSQL**

because transaction systems are naturally structured and relational.

Potential tables:

```text
users
merchants
customers
transactions
risk_scores
risk_rules
alerts
analyst_decisions
```

---

# 25. Functional Requirements

### FR-01

The system shall accept transaction data.

### FR-02

The system shall calculate a risk score for each transaction.

### FR-03

The system shall classify transactions as Low, Medium, or High risk.

### FR-04

The system shall generate an action recommendation.

### FR-05

The system shall provide reasons behind the risk decision.

### FR-06

The system shall store transaction risk history.

### FR-07

The dashboard shall display risk KPIs.

### FR-08

Users shall be able to inspect individual transactions.

### FR-09

Analysts shall be able to override recommendations.

### FR-10

The system shall record analyst decisions.

---

# 26. Non-Functional Requirements

## Performance

Risk scoring should ideally occur within:

**< 500 ms**

for the MVP demonstration environment.

## Reliability

The risk engine should gracefully handle invalid or incomplete transaction data.

## Security

Sensitive payment information should not be unnecessarily stored.

The prototype should use:

- Authentication
- Authorization
- HTTPS
- Secure API handling
- Data minimization

## Explainability

Every high-risk decision should have at least one understandable reason.

## Scalability

The architecture should allow future migration from a prototype to high-volume transaction processing.

---

# 27. Success Metrics

The product should not measure success only by model accuracy.

Fraud detection is an imbalanced classification problem, so accuracy can be misleading.

### ML Metrics

- Precision
- Recall
- F1 Score
- ROC-AUC
- PR-AUC
- False Positive Rate
- False Negative Rate

### Product Metrics

#### Fraud Detection Rate

Percentage of fraudulent transactions detected.

#### False Positive Rate

Percentage of legitimate transactions incorrectly flagged.

This is extremely important because excessive blocking damages customer experience.

#### Review Efficiency

Percentage reduction in transactions requiring manual investigation.

#### Decision Latency

Average time required to produce a risk decision.

#### Prevented Loss

Estimated financial loss prevented through blocked fraudulent transactions.

---

# 28. North Star Metric

The most important product metric should be:

## **Risk-Adjusted Loss Prevented**

Rather than simply maximizing the number of blocked transactions.

Why?

Because blocking everything would technically reduce fraud but destroy legitimate payments.

The platform should optimize the balance between:

**Fraud Prevention + Approval Rate + Customer Experience**

---

# 29. Example Success Target for MVP

For a prototype, reasonable demonstration targets could be:

- **≥85% recall** on the validation/test dataset
- **≥80% precision** for high-risk predictions
- Risk decision generated in **<500 ms**
- 100% of high-risk transactions have explainable reasons
- Dashboard accurately reflects transaction decisions
- Analysts can investigate a transaction in **<30 seconds**

These are product targets, not guarantees. Actual thresholds should be finalized after evaluating the selected dataset.

---

# 30. Key Product Risks

## Risk 1 — False Positives

The system may incorrectly identify legitimate transactions as fraudulent.

### Mitigation

Use multiple risk levels:

**Approve → Review → Block**

instead of simply:

**Fraud / Not Fraud**

---

## Risk 2 — Data Imbalance

Fraud transactions are usually much rarer than legitimate transactions.

### Mitigation

Use:

- Class weighting
- Appropriate sampling
- Precision/recall analysis
- PR-AUC
- Threshold tuning

---

## Risk 3 — Model Explainability

A complex model may produce good predictions but poor explanations.

### Mitigation

Use feature importance/SHAP-style explanations and combine them with explicit rule triggers.

---

## Risk 4 — Concept Drift

Fraud patterns change over time.

### Mitigation

Design the architecture to support future model retraining and monitoring.

---

# 31. What We Are Deliberately NOT Building in V1

This is an important strategic decision.

### Not building a complete payment gateway

The objective is **risk intelligence**, not payment processing.

### Not building a mobile application

A responsive web dashboard is sufficient.

### Not implementing sophisticated graph fraud detection

Graph-based fraud detection is powerful but unnecessary for demonstrating the MVP.

### Not building our own identity/KYC infrastructure

Use existing systems/data where necessary.

### Not building autonomous AI agents

The MVP should use AI for risk analysis, not create an unnecessarily complex agentic architecture.

### Not supporting every payment method

Start with a structured transaction schema.

### Not building real-time global fraud intelligence

Cross-merchant intelligence can come later.

### Not attempting 100% fraud detection

There is no perfect fraud detector.

The goal is **better risk-adjusted decisions**.

---

# 32. Version Roadmap

## V0 — Prototype

- Dataset
- ML model
- Risk score
- Basic API
- Basic dashboard

## V1 — MVP

- ML + rules
- Explainable risk score
- Transaction investigation
- Alerts
- Merchant dashboard
- Approve/Review/Block workflow

## V1.1

- Custom risk rules
- Analyst feedback
- Advanced analytics
- Model monitoring

## V2

- Behavioral profiling
- Device intelligence
- Anomaly detection
- Graph-based fraud detection

## V3

- Cross-merchant intelligence
- Adaptive models
- AI fraud investigation assistant
- Network-level risk intelligence

---

# 33. Example End-to-End Scenario

A customer attempts to make a ₹75,000 payment.

The system observes:

```text
Amount: ₹75,000
Customer average: ₹4,200
Account age: 3 days
Device: New
Failed attempts: 6
Transactions in last 10 minutes: 8
Location deviation: High
```

The ML model calculates:

```text
Fraud Probability: 0.91
```

The rule engine detects:

```text
HIGH_AMOUNT
NEW_DEVICE
HIGH_VELOCITY
MULTIPLE_FAILED_ATTEMPTS
NEW_ACCOUNT
```

The risk aggregator produces:

```text
Risk Score: 94/100
Risk Level: HIGH
Recommendation: BLOCK
```

The dashboard displays:

> **High-Risk Transaction Detected**

**Why?**

- Transaction is significantly above normal customer behavior.
- Device has not previously been associated with the account.
- Multiple failed attempts occurred recently.
- Transaction velocity is unusually high.
- Account is newly created.

This gives the analyst both the **decision** and the **evidence**.

---

# 34. Product Principles

The product should follow five principles.

### 1. Explain, Don't Just Predict

Every risk decision should be understandable.

### 2. Protect Revenue, Not Just Prevent Fraud

A legitimate ₹1 lakh customer should not be blocked simply because the transaction is large.

### 3. Human-in-the-Loop

AI should prioritize decisions; humans should handle ambiguous cases.

### 4. Risk Is a Spectrum

Fraud is not simply:

**YES / NO**

It is:

**LOW → MEDIUM → HIGH**

### 5. Start Narrow, Scale Intelligently

The MVP should solve one problem extremely well before expanding into a massive fraud ecosystem.

---

# 35. Final MVP Definition

If development time is limited, the entire product can be reduced to this:

```text
                 AI RISK MANAGER
                       │
                       ▼
              Transaction Received
                       │
                       ▼
                Feature Extraction
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
        Rule Engine          ML Model
             │                   │
             └─────────┬─────────┘
                       ▼
                  Risk Score
                    0–100
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
      APPROVE         REVIEW         BLOCK
                       │
                       ▼
                 WHY? / EXPLAIN
                       │
                       ▼
              Merchant Dashboard
                       │
                       ▼
                Analyst Decision
```

That is the **MVP**.

Everything else should be treated as expansion.

---

# 36. One-Line Product Pitch

> **AI Risk Manager is an explainable, real-time payment risk engine that combines machine learning and intelligent rules to detect suspicious transactions, score their risk, explain why they are risky, and recommend whether to approve, review, or block them.**

---

# 37. Strategic Positioning

The strongest positioning for the Razorpay track is not:

> "We built a fraud detection ML model."

That sounds like a conventional college ML project.

Instead:

> **"We built an intelligent payment risk decisioning layer that converts transaction signals into explainable, actionable decisions."**

That changes the conversation from **ML project** to **fintech product**.

The differentiator is the complete loop:

**Detect → Score → Explain → Decide → Investigate → Learn**

That is what makes the concept commercially meaningful.