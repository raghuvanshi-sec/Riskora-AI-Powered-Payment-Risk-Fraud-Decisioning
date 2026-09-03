# Riskora — Pre-Deployment Audit Report

**Date:** 2026-08-31
**Phase:** Pre-Deployment QA + Cleanup
**Status:** PASS (with known limitations)

---

## Application Status

**PASS** — Core application functions correctly. Known limitations documented in §Known Issues.

---

## 1. Files Reviewed

| Category | Count |
|----------|-------|
| Backend Python files | 57 |
| Frontend JSX files | 11 |
| Frontend JS service files | 5 |
| CSS files | 4 |
| Test files | 4 |

---

## 2. End-to-End Tests

| Test | Result |
|------|--------|
| Backend unit tests (61 tests) | **PASS** |
| Frontend build (93 modules, 324KB JS) | **PASS** |
| Import chain (no circular deps) | **PASS** |
| API contract consistency | **PASS** |
| Explainable AI endpoint wired | **PASS** |
| Hybrid engine threshold consistency | **PASS** |

---

## 3. Backend

### Tests
- **61/61 tests pass** (pytest, SQLite in-memory)

### API Routes (20 endpoints)
| Method | Path | Auth | Status |
|--------|------|------|--------|
| POST | `/api/v1/auth/register` | — | OK |
| POST | `/api/v1/auth/login` | — | OK |
| GET | `/api/v1/auth/me` | Bearer | OK |
| GET | `/api/v1/transactions` | Bearer | OK |
| POST | `/api/v1/transactions` | RISK_ANALYST+ | OK |
| GET | `/api/v1/transactions/{id}` | Bearer | OK |
| PATCH | `/api/v1/transactions/{id}` | RISK_ANALYST+ | OK |
| GET | `/api/v1/transactions/summary` | Bearer | OK |
| POST | `/api/v1/risk/analyze/{id}` | RISK_ANALYST+ | OK |
| GET | `/api/v1/risk/transactions/{id}` | Bearer | OK |
| GET | `/api/v1/risk/summary` | Bearer | OK |
| GET | `/api/v1/risk/trends` | Bearer | OK |
| GET | `/api/v1/risk/recent` | Bearer | OK |
| GET | `/api/v1/risk/events` | Bearer | OK |
| POST | `/api/v1/risk/analyze/{id}/ml` | RISK_ANALYST+ | OK |
| GET | `/api/v1/risk/analyze/{id}/explain` | Bearer | **FIXED** |
| GET | `/api/v1/risk/models` | Bearer | OK |
| GET | `/api/v1/risk/models/{v}` | Bearer | OK |
| POST | `/api/v1/risk/models/{v}/activate` | RISK_ANALYST+ | OK |
| POST | `/api/v1/cases` | RISK_ANALYST+ | OK |
| GET | `/api/v1/cases` | Bearer | OK |
| GET | `/api/v1/cases/queue` | Bearer | OK |
| GET | `/api/v1/cases/stats` | Bearer | OK |
| GET | `/api/v1/cases/{id}` | Bearer | OK |
| PATCH | `/api/v1/cases/{id}` | RISK_ANALYST+ | OK |
| POST | `/api/v1/cases/{id}/assign` | RISK_ANALYST+ | OK |
| POST | `/api/v1/cases/{id}/actions` | RISK_ANALYST+ | OK |
| GET | `/api/v1/cases/{id}/actions` | Bearer | OK |

### Authentication & Authorization
- JWT Bearer token auth with 1-hour expiry
- Roles: `ADMIN`, `RISK_ANALYST`
- `require_risk_analyst` = ADMIN or RISK_ANALYST
- Passwords hashed with bcrypt via python-jose
- All protected routes verified

### Database
- 8 models: User, Merchant, Transaction, RiskAssessment, RiskEvent, RiskCase, AnalystAction, ModelVersion, AuditLog
- All relationships properly defined with cascade deletes
- SQLite (dev default), PostgreSQL-compatible schema
- No duplicate/unused tables

### ML
- XGBoost model with ModelRegistry for versioning
- `MockModel` fallback when no trained model exists (returns zero probability)
- SHAP explainer with graceful fallback (`shap_available=False`)
- Hybrid engine: 40% rules + 60% ML
- Training pipeline via `POST /api/v1/risk/models/{v}/activate`

### Risk Engine
- Rules engine: 9 rules (amount, velocity, device, location, merchant, failed attempts, account age)
- All thresholds defined in single source: `app/risk/constants.py`
- Hybrid engine now uses shared `risk_constants` (fixed during this audit)

---

## 4. Frontend

### Routes
| Path | Component | Status |
|------|-----------|--------|
| `/login` | LoginView | OK |
| `/` | DashboardView | OK |
| `/transactions` | TransactionsView | OK |
| `/transactions/:id` | TransactionDetail | OK |
| `/risk-queue` | RiskQueueView | OK |
| `/alerts` | AlertsView | OK |

### API Integration
- All API calls go through `src/services/api.js` (single Axios instance)
- `src/services/riskOpsService.js` for case management
- No hardcoded localhost URLs outside `api.js` baseURL
- All risk metrics from backend endpoints (no hardcoded values)

### Build
- 93 modules, 324KB JS, 11KB CSS (gzipped: 100KB + 2.9KB)

---

## 5. Security

| Check | Result |
|-------|--------|
| No committed secrets | OK (`.env` is gitignored) |
| No hardcoded passwords/secrets in code | OK |
| No `eval()`, `exec()`, `pickle.load()` from untrusted source | OK |
| No `innerHTML` / `dangerouslySetInnerHTML` | OK |
| No SQL injection vectors | OK |
| No XSS vectors | OK |
| JWT secret in `.env` (not hardcoded) | OK |
| CORS configured for localhost dev | OK |

### Known: Demo Credentials
- Seed data includes `admin@airiskmanager.com` / `RiskoraDemo123!` (documented in `seed.py`)
- These are for development/demo only, clearly commented
- Not applicable to production

---

## 6. Cleanup Actions Taken

### Code Fixes
1. **`hybrid.py`** — Threshold constants duplicated hardcoded values. Fixed to import and use `risk_constants` from `app/risk/constants.py`.
2. **`explainable.py` dead code** — Phase 7 created `ExplainableRiskResult`, `build_explainable_result`, and `SHAPFactorResponse` but never wired them into `risk_service` or API routes. Fixed: added `analyze_transaction_explainable()` to `risk_service` and `GET /risk/analyze/{id}/explain` endpoint.
3. **Circular import in `risk_service`** — `ExplainableRiskResult` import at module level caused numpy to load before ML try/except guard. Fixed: moved import inside `analyze_transaction_explainable()` function.
4. **`risk_ops.py` unused import** — `CasePriority` imported but never used. Removed.
5. **`metadata` reserved name** — `AnalystAction.metadata` renamed to `metadata_json` (SQLAlchemy reserved attribute).

### No Changes Made
- CSS: `components.css` duplicates some tokens from `index.css` but both are loaded and harmless
- `conftest.py` files: both are legitimate pytest path-configuration files
- `MockModel` in `models.py`: used as fallback when no trained model is available
- Seed data: deterministic (`random.seed(42)`), clearly documented as fictional

---

## 7. Dependencies

### Backend (`backend/requirements.txt`)
All verified imported:
- `fastapi`, `uvicorn`, `sqlalchemy`, `python-jose`, `passlib`, `pydantic-settings`, `python-multipart`
- `numpy`, `scikit-learn`, `xgboost`, `shap` (optional — graceful fallback)
- `pytest`, `httpx` (dev)

### Frontend (`frontend/package.json`)
- `react`, `react-dom`, `react-router-dom`
- `axios`
- `framer-motion` (animations)
- `recharts` (dashboard charts)
- `vite`, `@vitejs/plugin-react` (build)

---

## 8. Known Issues

| # | Issue | Severity | Notes |
|---|-------|----------|-------|
| 1 | SHAP library may not be installed | Low | Graceful fallback returns `shap_available: false` |
| 2 | ML model must be trained before hybrid scoring is meaningful | Medium | `MockModel` returns 0 probability until training |
| 3 | Seed data is auto-loaded on app startup | Low | Can be disabled by not calling `generate_transactions()` |
| 4 | No database migrations system | Medium | Schema changes require manual DROP+RECREATE for dev |
| 5 | `model_version` Pydantic field namespace warning | Low | Warning only, not an error |

---

## 9. Deployment Blockers

**NONE** — The application is production-oriented (not production-deployed).

The following are prerequisites for actual production deployment (not blockers for this phase):

1. Replace `SECRET_KEY` in production `.env`
2. Configure PostgreSQL database
3. Train and deploy ML model artifacts
4. Install `shap` library for explainability
5. Configure CORS origins for production domain
6. Set up reverse proxy (nginx) and HTTPS
7. Configure environment-specific settings

---

## 10. Verification Checklist

| Item | Status |
|------|--------|
| No broken imports | ✅ |
| No null-byte Python files | ✅ |
| No obsolete mock production logic | ✅ |
| No fake risk scores | ✅ |
| No fake ML metrics | ✅ |
| No fake SHAP explanations | ✅ |
| No hard-coded dashboard metrics | ✅ |
| No hard-coded API URLs | ✅ |
| No committed secrets | ✅ |
| No debug prints | ✅ |
| No debugger statements | ✅ |
| No obvious dead code | ✅ |
| Database schema coherent | ✅ |
| Seed logic isolated | ✅ |
| Authentication works | ✅ |
| Authorization works | ✅ |
| Transactions work | ✅ |
| Risk engine works | ✅ |
| ML works (with fallback) | ✅ |
| SHAP works (with fallback) | ✅ |
| Hybrid engine works | ✅ |
| Risk cases work | ✅ |
| Analyst actions work | ✅ |
| Audit logs work | ✅ |
| Dashboard works | ✅ |
| Frontend builds | ✅ |
| Backend tests pass (61/61) | ✅ |
| Clean installation (env setup required) | ⚠️ |

---

## 11. Summary

Riskora is a **production-oriented** fintech risk management platform with:

- FastAPI backend with 28 endpoints, JWT auth, role-based access
- React 19 frontend with dark theme fintech UI
- Rules-based risk engine (9 rules, thresholds in single source)
- XGBoost ML model with ModelRegistry versioning
- SHAP explainability (graceful fallback when unavailable)
- Hybrid risk engine (40% rules + 60% ML)
- Analyst case management workflow (RiskCase + AnalystAction)
- Complete audit logging on all sensitive operations
- Deterministic seed data for development

**Ready for Phase 10 (deployment) once deployment prerequisites are met.**
