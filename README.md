# Riskora — AI-Powered Payment Risk Intelligence

A production-oriented full-stack fintech risk management platform that evaluates financial transactions in near real time, assigns risk scores (0–100), determines threat levels, and makes automated decisions (ALLOW / REVIEW / BLOCK) backed by explainable AI.

---

## Architecture

```
Client (React) ──► FastAPI Gateway ──► Risk Engine Service
                                              │
                     ┌─────────────────────────┼─────────────────────────┐
                     ▼                         ▼                         ▼
               Rules Engine          XGBoost ML Model          SHAP Explainer
               (9 rules)           (ModelRegistry)           (feature attribution)
                     │                         │                         │
                     ▼                         ▼                         ▼
               PostgreSQL/SQLite        PostgreSQL/SQLite        PostgreSQL/SQLite
```

**Technology:** React 19 + Vite · FastAPI · SQLAlchemy 2.0 · XGBoost · SHAP · JWT Auth

---

## Project Structure

```
backend/
├── app/
│   ├── api/routes/          # FastAPI route handlers
│   │   ├── auth.py          # /auth/register, /auth/login
│   │   ├── transactions.py  # CRUD + summary
│   │   ├── risk.py          # /risk/* endpoints
│   │   └── risk_ops.py      # /cases/* analyst workflow
│   ├── core/               # config, security, errors
│   ├── db/                 # database, seed data
│   ├── ml/                 # XGBoost, features, training, SHAP, hybrid scoring
│   ├── models/             # SQLAlchemy models (User, Transaction, RiskCase, etc.)
│   ├── risk/               # Rules engine, feature extractor, scoring, explainability
│   ├── schemas/            # Pydantic request/response models
│   └── services/           # Business logic (transaction, risk, risk_ops, audit, ml)
frontend/
├── src/
│   ├── auth/               # AuthContext, ProtectedRoute
│   ├── components/         # Reusable UI (EmptyState, ErrorState, Skeletons)
│   ├── services/           # API clients (api.js, transactionService, riskService, riskOpsService)
│   ├── views/              # Page components
│   │   ├── DashboardView    # Metrics, risk summary, recent transactions
│   │   ├── TransactionsView # Paginated transaction list with search/filter
│   │   ├── TransactionDetail# Signals, risk assessment, case management
│   │   ├── RiskQueueView    # Analyst review queue
│   │   ├── AlertsView       # Risk events and open cases
│   │   └── LoginView        # Authentication
│   ├── App.jsx             # Router + layout
│   ├── index.css            # Design tokens + global styles
│   ├── tokens.css           # Color, typography, spacing system
│   └── components.css       # Reusable component styles
docs/
├── pre-deployment-audit.md  # Full QA audit report
```

---

## Features

### Completed Phases

| Phase | Description |
| ------- | ------------- |
| 1–3 | Project foundation, PostgreSQL/SQLAlchemy, JWT authentication + RBAC |
| 4 | Transaction management: CRUD, search, pagination, summary |
| 5 | Rule-based risk engine: 9 rules (amount, velocity, device, location, merchant, failed attempts, account age) |
| 6 | XGBoost ML pipeline: feature engineering, ModelRegistry, training interface |
| 7 | SHAP explainability + hybrid engine (40% rules + 60% ML) |
| 8 | Analyst operations: RiskCase workflow, analyst actions, audit trail |

### Risk Engine

The rules engine evaluates every transaction against 9 rules:

| Rule | Trigger | Weight |
| ------ | --------- | -------- |
| `HIGH_AMOUNT` | amount > ₹75,000 | 20 |
| `UNUSUAL_AMOUNT` | amount > 5× previous | 25 |
| `HIGH_VELOCITY` | velocity > 6/hr | 15 |
| `NEW_DEVICE` | device_change = true | 15 |
| `LOCATION_CHANGE` | location_change = true | 12 |
| `HIGH_MERCHANT_RISK` | merchant_risk > 61 | 18 |
| `FAILED_ATTEMPTS` | failed_attempts ≥ 4 | 20 |
| `NEW_ACCOUNT` | account_age_days < 30 | 10 |
| `MULTIPLE_FAILED_ATTEMPTS` | failed_attempts ≥ 2 | 15 |

Thresholds: `LOW < 30`, `MEDIUM 30–69`, `HIGH ≥ 70`

### Hybrid Scoring

```
final_score = rules_score × 0.4 + ml_score × 0.6
```

ML score derived from XGBoost `fraud_probability × 100`. All thresholds use shared constants from `app/risk/constants.py`.

### Analyst Workflow

```
Transaction → Risk Assessment → Auto-created Case → Review Queue
    → Assign Analyst → Analyst Actions (ALLOW/BLOCK/ESCALATE/FLAG/DISMISS/ADD_NOTE)
    → Status transitions (OPEN → IN_PROGRESS → RESOLVED/ESCALATED/CLOSED)
    → Full audit log
```

---

## API Endpoints

| Method | Path | Auth | Description |
| -------- | ------ | ------ | ------------- |
| POST | `/api/v1/auth/register` | — | Register user |
| POST | `/api/v1/auth/login` | — | Login, returns JWT |
| GET | `/api/v1/auth/me` | Bearer | Current user |
| GET | `/api/v1/transactions` | Bearer | List with pagination/filter/sort |
| POST | `/api/v1/transactions` | RISK_ANALYST+ | Create transaction |
| GET | `/api/v1/transactions/{id}` | Bearer | Transaction detail |
| PATCH | `/api/v1/transactions/{id}` | RISK_ANALYST+ | Update transaction |
| GET | `/api/v1/transactions/summary` | Bearer | Aggregate metrics |
| POST | `/api/v1/risk/analyze/{id}` | RISK_ANALYST+ | Run rules-based analysis |
| POST | `/api/v1/risk/analyze/{id}/ml` | RISK_ANALYST+ | Run hybrid ML analysis |
| GET | `/api/v1/risk/analyze/{id}/explain` | Bearer | Full explainable result + SHAP |
| GET | `/api/v1/risk/summary` | Bearer | Risk level counts |
| GET | `/api/v1/risk/trends` | Bearer | Daily risk trends |
| GET | `/api/v1/risk/recent` | Bearer | Recent risk decisions |
| GET | `/api/v1/risk/events` | Bearer | Risk events |
| GET | `/api/v1/risk/models` | Bearer | List ML model versions |
| POST | `/api/v1/risk/models/{v}/activate` | RISK_ANALYST+ | Activate model version |
| POST | `/api/v1/cases` | RISK_ANALYST+ | Create case |
| GET | `/api/v1/cases` | Bearer | List cases |
| GET | `/api/v1/cases/queue` | Bearer | Review queue |
| GET | `/api/v1/cases/stats` | Bearer | Queue statistics |
| GET | `/api/v1/cases/{id}` | Bearer | Case detail |
| PATCH | `/api/v1/cases/{id}` | RISK_ANALYST+ | Update case |
| POST | `/api/v1/cases/{id}/assign` | RISK_ANALYST+ | Assign analyst |
| POST | `/api/v1/cases/{id}/actions` | RISK_ANALYST+ | Record analyst action |
| GET | `/api/v1/cases/{id}/actions` | Bearer | Case action history |

---

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- npm or yarn

### Backend

```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# Windows: .venv\Scripts\activate
# Linux/macOS: source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env
# Edit .env: set SECRET_KEY, DATABASE_URL, etc.

# Run the server
uvicorn app.main:app --reload --port 8000
```

The database (SQLite by default) and seed data are created automatically on first startup.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Frontend runs on `http://localhost:5173` and proxies `/api` to `http://localhost:8000`.

### Demo Credentials

On first startup, seed data creates:

| Email | Password | Role |
|-------|----------|------|
| `admin@airiskmanager.com` | `RiskoraDemo123!` | ADMIN |

### Training the ML Model

The ML model requires training before hybrid scoring is meaningful. Until then, `MockModel` returns 0 probability and the system operates on rules alone.

```bash
# In a Python shell with the venv activated:
from app.ml.training import train_model, TrainingConfig

config = TrainingConfig(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
)
model, metrics = train_model(config)
print(metrics)
```

Activate via: `POST /api/v1/risk/models/{version}/activate`

---

## Environment Variables

| Variable | Default | Description |
| ---------- | --------- | ------------- |
| `SECRET_KEY` | *(required)* | JWT signing key |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60` | JWT expiry |
| `DATABASE_URL` | `sqlite:///./airiskmanager.db` | PostgreSQL or SQLite |
| `BACKEND_CORS_ORIGINS` | `http://localhost:5173` | Allowed CORS origins |

---

## Testing

```bash
# Backend tests (61 tests)
cd backend
.venv\Scripts\python.exe -m pytest tests/ -v

# Frontend build
cd frontend
npm run build
```

---

## Security Notes

- Passwords hashed with bcrypt via `python-jose`
- JWT Bearer token authentication
- Role-based access: `ADMIN`, `RISK_ANALYST`
- All sensitive operations logged to `audit_logs` table
- Secrets stored in `.env`, not committed to git

**Do not use the default `SECRET_KEY` in production.**

---

## Deployment Prerequisites (not included in this codebase)

- [ ] Replace `SECRET_KEY` with a production value
- [ ] Configure PostgreSQL (remove SQLite)
- [ ] Train and deploy ML model artifact
- [ ] Install `shap` library for full explainability
- [ ] Set production CORS origins
- [ ] Configure reverse proxy (nginx) + HTTPS
- [ ] Set up CI/CD pipeline
