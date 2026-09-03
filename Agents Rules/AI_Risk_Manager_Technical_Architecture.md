# Technical Architecture Document — AI Risk Manager

**Product:** AI Risk Manager — Razorpay Track  
**Document Type:** Technical Architecture Document  
**Version:** MVP / Version 1.0  
**Architecture Style:** Modular monolith with ML risk engine  
**Primary Goal:** Build an explainable, real-time payment risk decisioning platform.

---

## 1. System Overview

AI Risk Manager is a payment-risk decisioning platform that receives transaction data, extracts behavioral features, evaluates deterministic risk rules and an ML model, combines their outputs into a risk score, explains the decision, and recommends:

- **APPROVE**
- **REVIEW**
- **BLOCK**

### High-Level Architecture

```text
                         ┌──────────────────────┐
                         │      Merchant        │
                         │      / Analyst       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │    React Frontend    │
                         │   Risk Dashboard     │
                         └──────────┬───────────┘
                                    │ HTTPS / REST
                                    ▼
                         ┌──────────────────────┐
                         │     FastAPI API      │
                         │ Authentication       │
                         │ Transaction APIs     │
                         │ Dashboard APIs       │
                         └──────────┬───────────┘
                                    │
                                    ▼
                    ┌───────────────────────────────┐
                    │       Risk Orchestrator       │
                    └───────────────┬───────────────┘
                                    │
                    ┌───────────────┼────────────────┐
                    ▼               ▼                ▼
             ┌────────────┐ ┌──────────────┐ ┌───────────────┐
             │ Rule Engine│ │  ML Model    │ │  Anomaly      │
             │            │ │  XGBoost     │ │  Detection    │
             └─────┬──────┘ └──────┬───────┘ └───────┬───────┘
                   │               │                 │
                   └───────────────┼─────────────────┘
                                   ▼
                         ┌──────────────────────┐
                         │   Risk Aggregator    │
                         │   Score 0–100        │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │ Explainability Layer │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │   Final Decision     │
                         │ APPROVE/REVIEW/BLOCK │
                         └──────────┬───────────┘
                                    ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         └──────────────────────┘
```

---

## 2. Recommended Tech Stack

| Layer | Technology | Reason |
|---|---|---|
| Frontend | React | Fast dashboard development |
| Language | JavaScript | Matches the current skillset |
| Build | Vite | Fast development and builds |
| Styling | Vanilla CSS | Simple and controllable |
| Charts | Recharts | Risk analytics |
| Backend | FastAPI | Excellent Python + ML integration |
| API | REST | Simple and demonstrable |
| Database | PostgreSQL | Strong relational transaction model |
| ORM | SQLAlchemy 2.x | Mature Python ORM |
| Migration | Alembic | Database versioning |
| ML | XGBoost | Strong tabular-data performance |
| ML utilities | Scikit-learn | Preprocessing and evaluation |
| Explainability | SHAP | Model explanations |
| Model storage | Joblib | Simple MVP model persistence |
| Authentication | JWT | Stateless authentication |
| Containers | Docker | Reproducible development/deployment |
| CI/CD | GitHub Actions | Automated testing/deployment |
| Backend testing | Pytest | Python testing |
| Frontend testing | Vitest | React testing |

### Stack Decision

For V1, keep the infrastructure intentionally simple:

```text
React
  +
FastAPI
  +
PostgreSQL
  +
XGBoost
  +
Docker
```

Do not introduce microservices, Kafka, Kubernetes, Redis clusters, graph databases, or complex MLOps infrastructure until scale genuinely requires them.

---

## 3. Frontend Architecture

### Core Technologies

- React
- JavaScript ES6+
- Vite
- React Router
- Axios
- Recharts
- Framer Motion
- Vanilla CSS

### Frontend Responsibilities

The frontend is responsible for:

- Authentication UI
- Merchant dashboard
- Transaction listing
- Transaction investigation
- Risk visualization
- Alerts
- Analytics
- Risk rule configuration
- Settings

The frontend should not contain business-critical risk logic. All risk calculations must happen on the backend.

---

## 4. Backend Architecture

### FastAPI

FastAPI is the primary application backend.

Responsibilities:

- REST API
- Authentication
- Authorization
- Transaction ingestion
- Risk evaluation
- Dashboard APIs
- Alert APIs
- Rule management
- Analytics
- Database access

### Backend Layering

```text
API Route
   ↓
Service Layer
   ↓
Risk Engine / Business Logic
   ↓
Repository / ORM
   ↓
PostgreSQL
```

This keeps HTTP handling separate from business logic.

---

## 5. Machine Learning Architecture

### Primary Model

**XGBoost Classifier**

XGBoost is recommended because payment-risk data is primarily structured/tabular data.

### Example Features

```text
transaction_amount
account_age
failed_attempts
transactions_last_5min
transactions_last_1hr
average_transaction_amount
amount_deviation
is_new_device
device_transaction_count
location_deviation
```

### Model Pipeline

```text
Raw Dataset
     ↓
Data Cleaning
     ↓
Feature Engineering
     ↓
Train/Test Split
     ↓
Model Training
     ↓
Evaluation
     ↓
Model Serialization
     ↓
Risk Probability
```

### ML Libraries

```text
pandas
numpy
scikit-learn
xgboost
joblib
shap
```

---

## 6. Database

### Database: PostgreSQL

PostgreSQL is recommended because payment transactions, customers, merchants, risk assessments, rules, and analyst decisions have strong relational relationships.

### ORM

Use:

```text
SQLAlchemy 2.x
```

### Database Migrations

Use:

```text
Alembic
```

---

# 7. Complete Project Structure

```text
ai-risk-manager/
│
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Makefile
│
├── frontend/
│   ├── package.json
│   ├── vite.config.js
│   ├── index.html
│   │
│   └── src/
│       ├── main.jsx
│       ├── App.jsx
│       │
│       ├── assets/
│       │
│       ├── components/
│       │   ├── common/
│       │   │   ├── Button.jsx
│       │   │   ├── Modal.jsx
│       │   │   ├── Badge.jsx
│       │   │   ├── Loader.jsx
│       │   │   └── EmptyState.jsx
│       │   │
│       │   ├── dashboard/
│       │   │   ├── RiskOverview.jsx
│       │   │   ├── RiskScoreCard.jsx
│       │   │   ├── RiskTrendChart.jsx
│       │   │   ├── TransactionChart.jsx
│       │   │   └── AlertPanel.jsx
│       │   │
│       │   ├── transactions/
│       │   │   ├── TransactionTable.jsx
│       │   │   ├── TransactionFilters.jsx
│       │   │   ├── TransactionDetails.jsx
│       │   │   └── RiskFactors.jsx
│       │   │
│       │   └── layout/
│       │       ├── Sidebar.jsx
│       │       ├── Navbar.jsx
│       │       └── DashboardLayout.jsx
│       │
│       ├── pages/
│       │   ├── Login.jsx
│       │   ├── Dashboard.jsx
│       │   ├── Transactions.jsx
│       │   ├── TransactionDetails.jsx
│       │   ├── Alerts.jsx
│       │   ├── Analytics.jsx
│       │   ├── Rules.jsx
│       │   └── Settings.jsx
│       │
│       ├── services/
│       │   ├── api.js
│       │   ├── authService.js
│       │   ├── transactionService.js
│       │   ├── riskService.js
│       │   └── dashboardService.js
│       │
│       ├── hooks/
│       │   ├── useAuth.js
│       │   ├── useTransactions.js
│       │   └── useRisk.js
│       │
│       ├── context/
│       │   └── AuthContext.jsx
│       │
│       ├── utils/
│       │   ├── formatCurrency.js
│       │   ├── formatDate.js
│       │   └── riskHelpers.js
│       │
│       └── styles/
│           ├── globals.css
│           └── variables.css
│
├── backend/
│   ├── requirements.txt
│   ├── Dockerfile
│   │
│   ├── app/
│   │   ├── main.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   ├── database.py
│   │   │   └── logging.py
│   │   │
│   │   ├── api/
│   │   │   ├── dependencies.py
│   │   │   │
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── transactions.py
│   │   │       ├── risk.py
│   │   │       ├── dashboard.py
│   │   │       ├── alerts.py
│   │   │       ├── rules.py
│   │   │       └── analytics.py
│   │   │
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── merchant.py
│   │   │   ├── customer.py
│   │   │   ├── device.py
│   │   │   ├── transaction.py
│   │   │   ├── risk_assessment.py
│   │   │   ├── risk_factor.py
│   │   │   ├── risk_rule.py
│   │   │   ├── alert.py
│   │   │   ├── analyst_decision.py
│   │   │   └── audit_log.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── auth.py
│   │   │   ├── transaction.py
│   │   │   ├── risk.py
│   │   │   ├── dashboard.py
│   │   │   ├── alert.py
│   │   │   └── rule.py
│   │   │
│   │   ├── services/
│   │   │   ├── auth_service.py
│   │   │   ├── transaction_service.py
│   │   │   ├── risk_service.py
│   │   │   ├── dashboard_service.py
│   │   │   └── alert_service.py
│   │   │
│   │   ├── risk_engine/
│   │   │   ├── orchestrator.py
│   │   │   ├── feature_engineering.py
│   │   │   ├── rule_engine.py
│   │   │   ├── ml_engine.py
│   │   │   ├── risk_aggregator.py
│   │   │   └── explainability.py
│   │   │
│   │   └── utils/
│   │       ├── validators.py
│   │       ├── constants.py
│   │       └── helpers.py
│   │
│   ├── migrations/
│   └── tests/
│       ├── test_auth.py
│       ├── test_transactions.py
│       ├── test_risk_engine.py
│       ├── test_rules.py
│       └── test_risk_api.py
│
├── ml/
│   ├── data/
│   │   ├── raw/
│   │   ├── processed/
│   │   └── sample/
│   │
│   ├── notebooks/
│   │   ├── 01_data_exploration.ipynb
│   │   ├── 02_feature_engineering.ipynb
│   │   ├── 03_model_training.ipynb
│   │   └── 04_model_evaluation.ipynb
│   │
│   ├── src/
│   │   ├── preprocessing.py
│   │   ├── features.py
│   │   ├── train.py
│   │   ├── evaluate.py
│   │   └── predict.py
│   │
│   ├── models/
│   │   └── risk_model.pkl
│   │
│   └── requirements.txt
│
├── docs/
│   ├── architecture.md
│   ├── api.md
│   ├── database.md
│   └── risk-engine.md
│
└── scripts/
    ├── seed_database.py
    ├── generate_transactions.py
    └── train_model.py
```

---

# 8. Database Schema

The core database contains:

```text
users
merchants
customers
devices
transactions
risk_assessments
risk_factors
risk_rules
alerts
analyst_decisions
audit_logs
```

---

## 8.1 Merchants

Represents a business using the platform.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| business_name | VARCHAR | Business name |
| email | VARCHAR | Business email |
| industry | VARCHAR | Business industry |
| status | VARCHAR | Active/inactive status |
| risk_threshold_low | INTEGER | Lower risk threshold |
| risk_threshold_high | INTEGER | Upper risk threshold |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

Example:

```text
risk_threshold_low = 30
risk_threshold_high = 70
```

Decision mapping:

```text
0–30   → APPROVE
31–70  → REVIEW
71–100 → BLOCK
```

---

## 8.2 Users

Stores people who access the platform.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| merchant_id | UUID | Foreign key to merchants |
| name | VARCHAR | User name |
| email | VARCHAR | Login email |
| password_hash | TEXT | Secure password hash |
| role | VARCHAR | ADMIN / ANALYST |
| is_active | BOOLEAN | Account status |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

Relationship:

```text
Merchant 1 ──── N Users
```

---

## 8.3 Customers

Represents customers making payments.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| merchant_id | UUID | Foreign key |
| external_customer_id | VARCHAR | Merchant's customer ID |
| email_hash | VARCHAR | Hashed email |
| account_created_at | TIMESTAMP | Account creation date |
| country | VARCHAR | Customer country |
| total_transactions | INTEGER | Transaction count |
| total_spend | DECIMAL | Total spending |
| average_transaction_amount | DECIMAL | Average transaction value |
| created_at | TIMESTAMP | Creation time |

Avoid unnecessarily storing sensitive customer data.

---

## 8.4 Devices

Tracks devices associated with customers.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| customer_id | UUID | Foreign key |
| device_fingerprint | VARCHAR | Device identifier |
| first_seen_at | TIMESTAMP | First observed |
| last_seen_at | TIMESTAMP | Most recent observation |
| transaction_count | INTEGER | Number of transactions |
| account_count | INTEGER | Number of associated accounts |
| risk_score | FLOAT | Device risk |

Example:

```text
One device
     ↓
20 different accounts
     ↓
Potential fraud signal
```

---

## 8.5 Transactions

The central transaction table.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| merchant_id | UUID | Foreign key |
| customer_id | UUID | Foreign key |
| device_id | UUID | Foreign key |
| external_transaction_id | VARCHAR | External transaction ID |
| amount | DECIMAL | Transaction amount |
| currency | VARCHAR | Currency code |
| payment_method | VARCHAR | CARD / UPI / etc. |
| status | VARCHAR | SUCCESS / FAILED / PENDING / REFUNDED |
| ip_address_hash | VARCHAR | Hashed IP |
| country | VARCHAR | Transaction country |
| transaction_timestamp | TIMESTAMP | Transaction time |
| failed_attempts | INTEGER | Recent failed attempts |
| created_at | TIMESTAMP | Creation time |

Relationships:

```text
Merchant ──── N Transactions
Customer ──── N Transactions
Device ────── N Transactions
```

---

## 8.6 Risk Assessments

Stores AI-generated risk evaluations.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| transaction_id | UUID | Foreign key |
| model_version | VARCHAR | Model used |
| fraud_probability | FLOAT | ML probability |
| risk_score | INTEGER | Score from 0–100 |
| risk_level | VARCHAR | LOW / MEDIUM / HIGH |
| recommended_action | VARCHAR | APPROVE / REVIEW / BLOCK |
| final_action | VARCHAR | Final action |
| processing_time_ms | INTEGER | Processing latency |
| created_at | TIMESTAMP | Assessment time |

Example:

```text
fraud_probability = 0.91
risk_score = 94
risk_level = HIGH
recommended_action = BLOCK
final_action = BLOCK
```

---

## 8.7 Risk Factors

Stores explanations behind the risk score.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| risk_assessment_id | UUID | Foreign key |
| factor_code | VARCHAR | Machine-readable code |
| factor_name | VARCHAR | Human-readable name |
| description | TEXT | Explanation |
| severity | VARCHAR | LOW / MEDIUM / HIGH |
| contribution | FLOAT | Contribution to risk |
| created_at | TIMESTAMP | Creation time |

Example:

```text
factor_code:
NEW_DEVICE

factor_name:
New Device

description:
Transaction originated from a previously unseen device.

severity:
HIGH
```

---

## 8.8 Risk Rules

Stores configurable risk rules.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| merchant_id | UUID | Foreign key |
| name | VARCHAR | Rule name |
| description | TEXT | Rule description |
| rule_type | VARCHAR | Rule category |
| condition | JSONB | Rule condition |
| action | VARCHAR | Action |
| score_modifier | INTEGER | Risk adjustment |
| is_active | BOOLEAN | Rule status |
| created_at | TIMESTAMP | Creation time |
| updated_at | TIMESTAMP | Last update |

Example:

```json
{
  "field": "failed_attempts",
  "operator": ">",
  "value": 5
}
```

Action:

```text
BLOCK
```

---

## 8.9 Alerts

Stores risk alerts.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| merchant_id | UUID | Foreign key |
| transaction_id | UUID | Optional transaction reference |
| type | VARCHAR | Alert type |
| severity | VARCHAR | Severity |
| title | VARCHAR | Alert title |
| message | TEXT | Alert details |
| is_read | BOOLEAN | Read status |
| created_at | TIMESTAMP | Creation time |

Example:

```text
type:
HIGH_RISK_TRANSACTION

severity:
CRITICAL
```

---

## 8.10 Analyst Decisions

Records human intervention.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| transaction_id | UUID | Foreign key |
| analyst_id | UUID | Foreign key to users |
| previous_action | VARCHAR | AI recommendation |
| final_action | VARCHAR | Analyst decision |
| reason | TEXT | Decision reason |
| created_at | TIMESTAMP | Decision time |

Example:

```text
AI:
BLOCK

Analyst:
APPROVE

Reason:
Customer verified through merchant support.
```

This data can become valuable feedback for future model improvement.

---

## 8.11 Audit Logs

Tracks important system actions.

| Field | Type | Description |
|---|---|---|
| id | UUID | Primary key |
| user_id | UUID | User performing action |
| action | VARCHAR | Action performed |
| entity_type | VARCHAR | Affected entity |
| entity_id | UUID | Affected record |
| metadata | JSONB | Additional details |
| created_at | TIMESTAMP | Event time |

Examples:

```text
LOGIN
TRANSACTION_REVIEWED
TRANSACTION_BLOCKED
RULE_UPDATED
SETTINGS_CHANGED
```

---

# 9. Database Relationship Diagram

```text
                    MERCHANT
                       │
          ┌────────────┼────────────┐
          │            │            │
          ▼            ▼            ▼
        USERS       CUSTOMERS     RISK_RULES
                       │
                       ▼
                    DEVICES
                       │
                       ▼
                  TRANSACTIONS
                       │
                       ▼
                RISK_ASSESSMENTS
                       │
                       ▼
                  RISK_FACTORS
                       │
                       ▼
                    ALERTS
                       │
                       ▼
                ANALYST_DECISIONS

USERS ────────────────┐
                      ▼
                 AUDIT_LOGS
```

---

# 10. Risk Engine

The risk engine is the core of the application.

Directory:

```text
backend/app/risk_engine/
```

Files:

```text
orchestrator.py
feature_engineering.py
rule_engine.py
ml_engine.py
risk_aggregator.py
explainability.py
```

---

## 10.1 Risk Orchestrator

Coordinates the complete evaluation process.

```text
Transaction
     ↓
Feature Engineering
     ↓
Rule Evaluation
     ↓
ML Prediction
     ↓
Risk Aggregation
     ↓
Explanation
     ↓
Final Decision
```

Pseudo-flow:

```python
def evaluate_transaction(transaction):

    features = extract_features(transaction)

    rule_result = evaluate_rules(features)

    ml_result = predict_ml(features)

    risk_score = aggregate(
        rule_result,
        ml_result
    )

    explanation = generate_explanation(
        rule_result,
        ml_result,
        features
    )

    decision = determine_action(
        risk_score
    )

    return RiskAssessment(...)
```

---

# 11. Risk Scoring

Every transaction receives a normalized score:

```text
0–100
```

### Risk Levels

| Score | Level | Action |
|---|---|---|
| 0–30 | LOW | APPROVE |
| 31–70 | MEDIUM | REVIEW |
| 71–100 | HIGH | BLOCK |

Thresholds should be configurable by merchant.

---

# 12. Risk Aggregation

Do not rely only on:

```text
ML probability × 100
```

Combine multiple signals.

Example:

```text
ML score                 70
Rule adjustments         +15
Behavioral anomaly       +10
────────────────────────────
Final risk score          95
```

Then clamp:

```python
max(0, min(score, 100))
```

This creates a hybrid risk decisioning system.

---

# 13. Rule Engine

The rule engine provides deterministic fraud checks.

Example:

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

The system therefore combines:

```text
Rules + ML = Risk Decision
```

---

# 14. Explainability Layer

The explainability system combines ML and rule signals.

### ML factors

```text
Transaction amount
Account age
Transaction velocity
Failed attempts
Device history
```

### Rule factors

```text
NEW_DEVICE
HIGH_AMOUNT
HIGH_VELOCITY
MULTIPLE_FAILED_ATTEMPTS
NEW_ACCOUNT
```

### User-facing output

```text
HIGH RISK

Why?

• Transaction amount is significantly above normal.
• Device has not previously been associated with this account.
• 7 transactions occurred within the last 10 minutes.
• 5 previous payment attempts failed.
```

---

# 15. API Architecture

Base URL:

```text
/api/v1
```

### Authentication

```text
POST /api/v1/auth/login
POST /api/v1/auth/register
GET  /api/v1/auth/me
```

### Transactions

```text
GET  /api/v1/transactions
GET  /api/v1/transactions/{id}
```

### Risk

```text
POST /api/v1/risk/evaluate
GET  /api/v1/risk/{transaction_id}
```

### Dashboard

```text
GET /api/v1/dashboard/overview
GET /api/v1/dashboard/trends
```

### Alerts

```text
GET  /api/v1/alerts
PATCH /api/v1/alerts/{id}/read
```

### Rules

```text
GET    /api/v1/rules
POST   /api/v1/rules
PATCH  /api/v1/rules/{id}
DELETE /api/v1/rules/{id}
```

### Analytics

```text
GET /api/v1/analytics/overview
GET /api/v1/analytics/fraud
```

---

# 16. Core Risk API

## Endpoint

```text
POST /api/v1/risk/evaluate
```

### Request

```json
{
  "transaction_id": "txn_123",
  "customer_id": "cust_123",
  "amount": 75000,
  "currency": "INR",
  "payment_method": "CARD",
  "device_id": "device_456",
  "failed_attempts": 6,
  "country": "IN"
}
```

### Response

```json
{
  "transaction_id": "txn_123",
  "risk_score": 94,
  "risk_level": "HIGH",
  "fraud_probability": 0.91,
  "recommended_action": "BLOCK",
  "risk_factors": [
    {
      "name": "New Device",
      "severity": "HIGH"
    },
    {
      "name": "High Transaction Velocity",
      "severity": "HIGH"
    },
    {
      "name": "Unusual Transaction Amount",
      "severity": "MEDIUM"
    }
  ]
}
```

---

# 17. Environment Variables

Create:

```text
.env
```

Never commit this file to Git.

Create:

```text
.env.example
```

for documentation.

### Backend `.env`

```env
APP_NAME=AI Risk Manager
APP_ENV=development
DEBUG=true

DATABASE_URL=postgresql://postgres:password@localhost:5432/ai_risk_manager

JWT_SECRET_KEY=change_me
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60

MODEL_PATH=./ml/models/risk_model.pkl

CORS_ORIGINS=http://localhost:5173

LOG_LEVEL=INFO
```

---

# 18. Frontend Environment Variables

Create:

```text
frontend/.env
```

Example:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### Important

Never put secrets into frontend variables beginning with:

```text
VITE_
```

Frontend variables are exposed to the browser.

---

# 19. Docker Architecture

For local development:

```text
docker-compose.yml
```

Services:

```text
Frontend
Backend
PostgreSQL
```

Architecture:

```text
┌───────────────────────┐
│ React Container       │
│ Port 5173             │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ FastAPI Container     │
│ Port 8000             │
└───────────┬───────────┘
            │
            ▼
┌───────────────────────┐
│ PostgreSQL Container  │
│ Port 5432             │
└───────────────────────┘
```

For the hackathon MVP, this is sufficient.

---

# 20. Security Requirements

Because this is a financial-risk product, security must be part of the architecture.

### Authentication

Use JWT-based authentication.

### Authorization

Roles:

```text
ADMIN
ANALYST
```

### Password Storage

Never store plaintext passwords.

Store:

```text
password_hash
```

### Sensitive Payment Data

Do not store:

- Raw card numbers
- CVV
- Full payment credentials

Use mock/tokenized identifiers for the prototype.

### API Security

Use HTTPS in production.

### Database Security

Use SQLAlchemy/parameterized queries.

### Logging

Never log sensitive payment information.

---

# 21. Model Versioning

Every risk assessment should record the model version.

Example:

```text
risk_model_v1.0
```

Future versions:

```text
risk_model_v1.1
risk_model_v2.0
```

This allows the system to answer:

> Which model generated this decision?

This is important for reproducibility and debugging.

---

# 22. Model Monitoring

Eventually monitor:

```text
Precision
Recall
F1
False Positive Rate
False Negative Rate
Prediction Distribution
Feature Drift
Model Drift
```

For MVP, expose basic model metrics through an admin/analytics screen rather than building a complete MLOps platform.

---

# 23. Development Order

Build vertically rather than attempting the entire application at once.

## Phase 1 — Foundation

```text
Repository
   ↓
FastAPI
   ↓
PostgreSQL
   ↓
SQLAlchemy
   ↓
Alembic
   ↓
Authentication
```

## Phase 2 — Data Layer

```text
Merchant
   ↓
Customer
   ↓
Device
   ↓
Transaction
```

## Phase 3 — ML

```text
Dataset
   ↓
EDA
   ↓
Feature Engineering
   ↓
XGBoost
   ↓
Evaluation
   ↓
Model Export
```

## Phase 4 — Risk Engine

```text
Transaction
   ↓
Features
   ↓
Rules
   ↓
ML
   ↓
Risk Score
   ↓
Explanation
```

## Phase 5 — APIs

Build:

```text
POST /risk/evaluate
GET /transactions
GET /transactions/{id}
GET /dashboard/overview
```

## Phase 6 — Dashboard

Build:

```text
Login
   ↓
Dashboard
   ↓
Transactions
   ↓
Transaction Details
   ↓
Risk Explanation
```

## Phase 7 — Advanced Features

Then add:

```text
Alerts
Rules
Analytics
Analyst Feedback
```

---

# 24. Features to Avoid in V1

Do not initially add:

```text
Kubernetes
Kafka
Redis Cluster
Microservices
Graph Database
LLM Agents
Complex Event Streaming
Feature Store
Airflow
MLflow
Terraform
Service Mesh
```

These can be introduced later if scale or product requirements justify them.

---

# 25. Future Scalable Architecture

If transaction volume eventually becomes very large:

```text
                    API Gateway
                         │
                         ▼
                Transaction Service
                         │
                         ▼
                  Event Streaming
                      Kafka
                         │
        ┌────────────────┼────────────────┐
        ▼                ▼                ▼
   Feature Service   Rule Engine      ML Service
        │                │                │
        └────────────────┼────────────────┘
                         ▼
                  Risk Decision Engine
                         │
               ┌─────────┴─────────┐
               ▼                   ▼
          PostgreSQL            Redis
               │
               ▼
          Analytics Layer
```

This is a future architecture, not the V1 implementation.

---

# 26. Example End-to-End Scenario

A customer attempts a ₹75,000 payment.

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

ML model:

```text
Fraud Probability: 0.91
```

Rule engine:

```text
HIGH_AMOUNT
NEW_DEVICE
HIGH_VELOCITY
MULTIPLE_FAILED_ATTEMPTS
NEW_ACCOUNT
```

Risk aggregator:

```text
Risk Score: 94/100
Risk Level: HIGH
Recommendation: BLOCK
```

Dashboard:

```text
HIGH-RISK TRANSACTION DETECTED

Why?

• Transaction amount is significantly above normal.
• Device has not previously been associated with the account.
• Multiple failed attempts occurred recently.
• Transaction velocity is unusually high.
• Account is newly created.
```

---

# 27. Final Recommended V1 Architecture

```text
                         ┌─────────────────┐
                         │     REACT       │
                         │    Dashboard    │
                         └────────┬────────┘
                                  │
                                  ▼
                         ┌─────────────────┐
                         │     FASTAPI     │
                         │      REST       │
                         └────────┬────────┘
                                  │
                                  ▼
                    ┌─────────────────────────┐
                    │    RISK ORCHESTRATOR    │
                    └────────────┬────────────┘
                                 │
                 ┌───────────────┼────────────────┐
                 ▼               ▼                ▼
           Feature Engine   Rule Engine      XGBoost
                 │               │                │
                 └───────────────┼────────────────┘
                                 ▼
                       ┌──────────────────┐
                       │ Risk Aggregator  │
                       └────────┬─────────┘
                                ▼
                       ┌──────────────────┐
                       │ Explainability   │
                       │      SHAP        │
                       └────────┬─────────┘
                                ▼
                    ┌─────────────────────────┐
                    │ APPROVE / REVIEW / BLOCK│
                    └────────────┬────────────┘
                                 ▼
                       ┌──────────────────┐
                       │   PostgreSQL     │
                       └──────────────────┘
```

---

# 28. Architectural Principles

## 1. Explain, Don't Just Predict

Every significant risk decision should be understandable.

## 2. Protect Revenue, Not Just Prevent Fraud

The system should balance fraud prevention with legitimate transaction approval.

## 3. Human-in-the-Loop

AI should prioritize and recommend; analysts should handle ambiguous cases.

## 4. Risk Is a Spectrum

Use:

```text
LOW → MEDIUM → HIGH
```

rather than simply:

```text
FRAUD / NOT FRAUD
```

## 5. Start Narrow, Scale Intelligently

The MVP should solve payment-risk decisioning well before expanding into a complete fraud ecosystem.

---

# 29. Final Architecture Decision

For the Razorpay AI Risk Manager MVP, use:

```text
Frontend:
React + JavaScript + Vite

Backend:
Python + FastAPI

Database:
PostgreSQL + SQLAlchemy + Alembic

ML:
XGBoost + Scikit-learn

Explainability:
SHAP

Authentication:
JWT

Infrastructure:
Docker

Testing:
Pytest + Vitest

Architecture:
Modular Monolith
```

### Core Product Pipeline

```text
Detect
   ↓
Score
   ↓
Explain
   ↓
Decide
   ↓
Investigate
   ↓
Learn
```

### Core Architectural Principle

> **Keep the infrastructure simple. Make the intelligence impressive.**

The strongest technical story is not that the project uses many technologies. It is that a suspicious transaction can pass through **feature extraction → rules → ML → risk score → explanation → decision**, with every step traceable and understandable.
