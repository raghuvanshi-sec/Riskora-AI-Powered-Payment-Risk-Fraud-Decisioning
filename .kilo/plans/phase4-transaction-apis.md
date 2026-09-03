# Phase 4 — Transaction Management + Transaction APIs

Scope: make transactions a real backend-driven feature with CRUD APIs, a service layer,
deterministic synthetic seed data, and a frontend that consumes the API instead of mocks.
Risk scoring / ML / SHAP are explicitly out of scope for this phase.

## Finalized decisions (from user)

1. `POST /transactions` body `user_id`/`merchant_id` are **int** (matching the DB FKs).
2. Seed data: **deterministic generator** with `random.seed(42)`, fictional customers/merchants,
   100-300 synthetic transactions. No hand-written hundreds of rows.
3. Authorization: **RISK_ANALYST + ADMIN** may create transactions; any authenticated active
   user may read. Admin only for any admin-only operations.

## Existing state (verified)

- Backend: `app/main.py`, `app/api/routes/__init__.py` (only `/auth`), `app/api/deps.py`,
  `app/db/`, `app/models/*` (User, Merchant, Transaction, RiskAssessment, RiskEvent,
  ModelVersion, AuditLog), `app/schemas/*`, `app/core/*`.
- Frontend: `frontend/src/App.jsx` imports `LoginView` from `./views/LoginView.jsx` — file EXISTS.
  All 4 views use hardcoded `mockTransactions`. No API calls anywhere.
- Tests: `tests/test_auth.py`, `tests/test_db.py` — use in-memory SQLite +
  `app.dependency_overrides[get_db]` pattern. Reuse this for transaction tests.
- `requirements.txt` missing `pydantic-settings` (used by `app/core/config.py`).

## File plan

### Backend — new
- `backend/app/services/transaction_service.py` — all DB/business logic for transactions.
- `backend/app/api/routes/transactions.py` — router, thin handlers.
- `backend/app/db/seed_transactions.py` — deterministic generator, 150-250 records.
- `backend/tests/test_transactions.py` — creation, retrieval, filtering, sorting,
  pagination, authz, validation, uniqueness.
- `backend/alembic/` + `alembic.ini` — migrations (create tables if missing).

### Backend — modified
- `backend/app/api/routes/__init__.py` — include transactions router.
- `backend/app/schemas/transaction.py` — add `TransactionCreate`, `TransactionUpdate`,
  `PaginatedResponse`, `TransactionSummary`, `TransactionDetail` (risk fields Optional/null).
- `backend/requirements.txt` — add pydantic-settings, pandas (seed only).
- `backend/app/db/seed.py` — call transaction generator.

### Frontend — new
- `frontend/src/services/transactionService.js` — thin wrapper over `api` (reuse axios config).
- `frontend/src/views/TransactionsView.jsx` — rewrite to consume API, keep Riskora design.
- `frontend/src/views/TransactionDetail.jsx` — new detail view.
- `frontend/src/components/LoadingSkeleton.jsx`, `ErrorState.jsx`, `EmptyState.jsx`.

### Frontend — modified
- `frontend/src/App.jsx` — register new routes.

## Detailed implementation order

1. Schema layer — add create/update/pagination/summary/detail schemas. Risk fields are
   `Optional` and rendered as null/"Pending Analysis" — never fabricated.
2. Service layer — `transaction_service.py` with create/get/list/patch, FK validation,
   allowlisted sort, DB-level pagination/filter, eager loading to avoid N+1.
3. Routes — `transactions.py` wired into `__init__.py`, auth required on all mutating
   and reading endpoints; audit events for CREATED/ UPDATED.
4. Seed — `seed_transactions.py` with `random.seed(42)`, fictional 20 customers,
   20 merchants, device pool, deterministic amounts/flags.
5. Tests — `test_transactions.py` covering all spec cases.
6. Frontend — service + views + components, replace mocks, loading/empty/error states.
7. Verify — run pytest, `npm run build`, curl smoke checks on all 6 endpoints.

## Boundaries

- No risk scoring, ML, SHAP, or LLM logic anywhere in this phase.
- No hard delete of transactions.
- No fake API responses — real DB all the way.
- Preserve existing Riskora visual design; do not redesign dashboard.

## Validation

- `pytest` passes.
- `npm run build` succeeds, no console errors.
- Smoke: `GET /health`, `GET /health/db`, `GET /transactions`, `GET /transactions/{id}`,
  `POST /transactions`, `PATCH /transactions/{id}` with auth.
- DB contains realistic synthetic transactions.
- Existing dashboard still renders.