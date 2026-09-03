# AI Risk Manager — Feature Ticket List

**Product:** AI Risk Manager — Razorpay Track  
**Source:** Product Requirements Document (PRD), MVP / Version 1.0

This ticket list converts the supplied PRD into buildable engineering tasks. Each ticket is written so it can be pasted into an AI coding tool with minimal modification.

## Priority Definitions
- **must-have for launch** — required for the MVP acceptance path.
- **should-have** — valuable for the MVP/early production version but can be deferred if time is constrained.
- **nice-to-have** — post-MVP capability.

## Recommended Build Order
1. Foundation: ARM-001 → ARM-005
2. Data + ingestion: ARM-006 → ARM-008
3. Risk engine: ARM-009 → ARM-014
4. Core UI: ARM-015 → ARM-021
5. Decisions + alerts: ARM-022 → ARM-026
6. Hardening and security: ARM-036 → ARM-045
7. Expansion: ARM-027 → ARM-035

---

## ARM-001 — Initialize React Frontend

**Priority:** `must-have for launch`

### AI Coding Prompt
Create the React JavaScript frontend foundation for AI Risk Manager. Use a maintainable feature-oriented structure, React Router, centralized styling/design tokens, and environment-based API configuration. Do not use TypeScript.

### Acceptance Criteria
- [ ] App starts successfully in development.
- [ ] Routes can be added without restructuring the app.
- [ ] API base URL is read from environment configuration.
- [ ] No secrets are hard-coded.
- [ ] A basic application shell renders successfully.

### Dependencies
None

---

## ARM-002 — Initialize FastAPI Backend

**Priority:** `must-have for launch`

### AI Coding Prompt
Create the Python FastAPI backend foundation for the AI Risk Manager MVP. Add versioned API routing, configuration management, database integration hooks, CORS configuration, health checking, and structured error responses.

### Acceptance Criteria
- [ ] Backend starts successfully.
- [ ] GET /api/v1/health returns a successful health response.
- [ ] API routes are versioned under /api/v1.
- [ ] Configuration is loaded from environment variables.
- [ ] Errors follow one documented JSON structure.

### Dependencies
None

---

## ARM-003 — Configure PostgreSQL Data Layer

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement the PostgreSQL data layer for merchants, users, customers, transactions, risk assessments, alerts, rules, and analyst decisions. Use migrations and enforce relational integrity.

### Acceptance Criteria
- [ ] Database connects successfully.
- [ ] Required MVP tables and relationships exist.
- [ ] Primary and foreign keys are enforced.
- [ ] Timestamps are stored consistently.
- [ ] Migrations can create the schema from an empty database.

### Dependencies
ARM-002

---

## ARM-004 — Implement Authentication and Authorization

**Priority:** `must-have for launch`

### AI Coding Prompt
Build secure authentication for merchants and risk users. Implement login/session handling and role-based authorization for Merchant, Fraud Analyst, Risk Operations Manager, and Admin capabilities defined by the security requirements.

### Acceptance Criteria
- [ ] Unauthenticated users cannot access protected APIs/pages.
- [ ] Valid users can authenticate and establish a session.
- [ ] Invalid credentials return a safe error.
- [ ] Protected endpoints enforce role permissions server-side.
- [ ] Logout invalidates the active session/token as designed.

### Dependencies
ARM-002, ARM-003

---

## ARM-005 — Create Shared API Client and Error Contract

**Priority:** `must-have for launch`

### AI Coding Prompt
Create a frontend API service layer that centralizes HTTP configuration, authentication, JSON parsing, request IDs, timeouts, and normalized error handling. Do not make raw API calls directly throughout UI components.

### Acceptance Criteria
- [ ] All frontend API calls use the shared client.
- [ ] 401, 403, 404, 409, 422, 429, 500, 503 and network errors map to usable UI states.
- [ ] Request IDs are retained for support/error messages where available.
- [ ] Secrets are never exposed in frontend configuration.

### Dependencies
ARM-001, ARM-002

---

## ARM-006 — Define Transaction Ingestion Schema

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement the canonical transaction input model for transaction ID, amount, currency, timestamp, customer/account ID, payment method, device information, IP/location information, history-derived fields, and failed attempts. Validate required and optional fields.

### Acceptance Criteria
- [ ] Valid transactions are accepted.
- [ ] Invalid types/required fields return validation errors.
- [ ] Amounts and currency are validated safely.
- [ ] Sensitive payment data not required for risk scoring is rejected or omitted.
- [ ] The schema is documented and versioned.

### Dependencies
ARM-002, ARM-003

---

## ARM-007 — Build Transaction Ingestion API

**Priority:** `must-have for launch`

### AI Coding Prompt
Create an authenticated API endpoint that receives a transaction and persists it before risk evaluation. Make the operation safe against duplicate transaction IDs where required.

### Acceptance Criteria
- [ ] POST transaction endpoint accepts the canonical schema.
- [ ] Transaction is persisted with merchant ownership.
- [ ] Duplicate transaction behavior is deterministic/idempotent.
- [ ] A successful response contains the transaction identifier and processing status.
- [ ] Unauthorized users cannot ingest into another merchant's data.

### Dependencies
ARM-003, ARM-004, ARM-006

---

## ARM-008 — Build Feature Extraction Pipeline

**Priority:** `must-have for launch`

### AI Coding Prompt
Build the feature extraction layer that converts raw transaction/customer/device/network/history data into model-ready features such as transaction velocity, amount deviation, account age, failed attempts, new device indicator, and geographic deviation.

### Acceptance Criteria
- [ ] Features are generated deterministically from supplied data.
- [ ] Missing optional fields are handled without crashing.
- [ ] Feature names and types are versioned.
- [ ] Historical features are computed using only information available before the decision timestamp.
- [ ] Feature generation can be reused by inference and future training pipelines.

### Dependencies
ARM-007, ARM-003

---

## ARM-009 — Train and Package XGBoost Risk Model

**Priority:** `must-have for launch`

### AI Coding Prompt
Train an initial tabular fraud-risk model using the approved transaction dataset. Evaluate precision, recall, F1, ROC-AUC, PR-AUC, false-positive rate, and false-negative rate. Package the selected model and preprocessing artifacts for backend inference.

### Acceptance Criteria
- [ ] Training and evaluation are reproducible.
- [ ] A held-out validation/test set is used.
- [ ] Model metrics are recorded.
- [ ] Preprocessing used during training is persisted with the model.
- [ ] A model version is assigned.
- [ ] Inference can load the exact packaged model artifact.

### Dependencies
ARM-008

---

## ARM-010 — Implement ML Risk Inference Service

**Priority:** `must-have for launch`

### AI Coding Prompt
Create a backend inference service that accepts model-ready features and returns fraud probability plus model version. Keep the ML implementation behind a clean service interface so the model can be replaced later.

### Acceptance Criteria
- [ ] Valid feature input produces a probability in the expected range.
- [ ] Model version is returned.
- [ ] Inference failures are handled safely.
- [ ] The frontend never calls the model directly.
- [ ] Inference latency is measured for the MVP target.

### Dependencies
ARM-009, ARM-008

---

## ARM-011 — Implement Rule-Based Risk Engine

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement deterministic risk rules for high amount versus normal behavior, failed attempts, new device plus high amount, and transaction velocity. Return triggered rules and their contribution/impact metadata.

### Acceptance Criteria
- [ ] Rules can evaluate a transaction deterministically.
- [ ] Each triggered rule identifies itself and provides a human-readable explanation.
- [ ] Rule failures do not silently produce a decision.
- [ ] Rules can be enabled/disabled through configuration.
- [ ] Rule evaluation is logged with the risk assessment.

### Dependencies
ARM-008, ARM-003

---

## ARM-012 — Build Risk Aggregation and Scoring

**Priority:** `must-have for launch`

### AI Coding Prompt
Combine ML fraud probability and deterministic rule signals into the product risk score from 0–100. Implement Low, Medium, and High categories and configurable action thresholds. Keep scoring logic centralized and versioned.

### Acceptance Criteria
- [ ] Every evaluated transaction receives a 0–100 risk score.
- [ ] Score maps to Low/Medium/High according to configured thresholds.
- [ ] Recommended action is Approve, Review, or Block.
- [ ] Scoring is deterministic for identical versioned inputs.
- [ ] Score and recommendation include model/rule versions.
- [ ] The authoritative score is generated only by the backend.

### Dependencies
ARM-010, ARM-011

---

## ARM-013 — Create Explainability Layer

**Priority:** `must-have for launch`

### AI Coding Prompt
Generate plain-English explanations for risk decisions using top model signals and triggered deterministic rules. Avoid claiming certainty that a transaction is fraudulent.

### Acceptance Criteria
- [ ] Every high-risk assessment has at least one understandable reason.
- [ ] Reasons identify the relevant signal and supporting value where available.
- [ ] Rule-trigger explanations are included.
- [ ] Model explanations are presented as contributing signals, not absolute proof.
- [ ] Explanations are persisted with the assessment.

### Dependencies
ARM-012

---

## ARM-014 — Create Risk Evaluation API

**Priority:** `must-have for launch`

### AI Coding Prompt
Expose the transaction risk evaluation workflow through a versioned FastAPI endpoint. The endpoint should retrieve transaction context, extract features, run rules and ML inference, aggregate the score, generate explanations, and persist the risk assessment.

### Acceptance Criteria
- [ ] A valid transaction can be evaluated end-to-end.
- [ ] Response contains risk score, risk level, recommendation, model version, and risk factors.
- [ ] Assessment is persisted.
- [ ] Repeated evaluation behavior is explicitly handled.
- [ ] Errors identify a safe request ID without exposing internals.

### Dependencies
ARM-007, ARM-008, ARM-010, ARM-011, ARM-012, ARM-013

---

## ARM-015 — Build Application Shell and Navigation

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement the authenticated fintech dashboard shell with sidebar/top navigation and routes for Dashboard, Transactions, Risk Queue, Alerts, Analytics, Risk Rules, and Settings. Enforce frontend route protection while keeping backend authorization authoritative.

### Acceptance Criteria
- [ ] Authenticated users see the application shell.
- [ ] Unauthenticated users are redirected to login.
- [ ] Navigation highlights the active route.
- [ ] Unauthorized navigation/actions are not presented where role restrictions are known.
- [ ] Responsive behavior works on desktop and mobile.

### Dependencies
ARM-001, ARM-004

---

## ARM-016 — Build Dashboard Summary API

**Priority:** `must-have for launch`

### AI Coding Prompt
Create APIs for dashboard KPIs: total transactions, high-risk transactions, blocked transactions, review transactions, fraud rate, average risk score, and estimated prevented loss where the underlying data supports it.

### Acceptance Criteria
- [ ] KPI endpoint returns merchant-scoped values.
- [ ] Period filters are supported for the MVP dashboard.
- [ ] Metrics are computed consistently from stored data.
- [ ] Unsupported/insufficient prevented-loss data is clearly represented rather than fabricated.

### Dependencies
ARM-003, ARM-014

---

## ARM-017 — Build Risk Dashboard UI

**Priority:** `must-have for launch`

### AI Coding Prompt
Create the main dashboard showing KPI cards, risk distribution, risk trend, high-risk transaction queue, and alerts using the frontend design system. Prioritize scanability and clear risk semantics.

### Acceptance Criteria
- [ ] Dashboard loads backend data.
- [ ] KPI cards display correct values.
- [ ] Risk distribution and trend render from API data.
- [ ] High-risk transactions link to investigation details.
- [ ] Loading, empty, error, and stale-data states exist.
- [ ] No dashboard metric is calculated independently in a way that conflicts with the backend.

### Dependencies
ARM-015, ARM-016, ARM-005

---

## ARM-018 — Build Transactions List API

**Priority:** `must-have for launch`

### AI Coding Prompt
Create a merchant-scoped transaction listing API with server-side pagination, search, sorting, and filters for risk level, status, amount, date, and payment method.

### Acceptance Criteria
- [ ] Pagination is server-side.
- [ ] Search supports transaction/customer identifiers permitted by the product.
- [ ] Filters work together.
- [ ] Sorting is deterministic.
- [ ] Responses include pagination metadata.
- [ ] Results cannot cross merchant authorization boundaries.

### Dependencies
ARM-003, ARM-004

---

## ARM-019 — Build Transactions Table UI

**Priority:** `must-have for launch`

### AI Coding Prompt
Build the transactions screen with search, filters, pagination, risk score, risk level, status, amount, timestamp, and links to transaction details.

### Acceptance Criteria
- [ ] Users can search and filter transactions.
- [ ] Pagination works without loading all records.
- [ ] Risk level is communicated by label and not color alone.
- [ ] Loading, empty, error, and no-results states exist.
- [ ] Clicking a row/action opens the correct transaction.

### Dependencies
ARM-015, ARM-018, ARM-005

---

## ARM-020 — Build Transaction Details API

**Priority:** `must-have for launch`

### AI Coding Prompt
Create an endpoint returning transaction information, customer context, risk assessment, triggered rules, explanations, relevant history, and decision history while respecting merchant and role permissions.

### Acceptance Criteria
- [ ] Authorized users can retrieve an owned transaction.
- [ ] Response includes risk score/level when evaluated.
- [ ] Risk factors and triggered rules are available.
- [ ] Decision history is included.
- [ ] Unauthorized cross-merchant access is denied without leaking record existence.

### Dependencies
ARM-014, ARM-003, ARM-004

---

## ARM-021 — Build Transaction Investigation UI

**Priority:** `must-have for launch`

### AI Coding Prompt
Create the transaction investigation page with transaction details, risk score, AI explanation, risk factors, triggered rules, customer information, relevant history, and recommended action. Provide clear Approve, Review, and Block actions according to permissions.

### Acceptance Criteria
- [ ] Analyst can open a transaction from the list.
- [ ] Risk score and explanation are visible.
- [ ] Top risk factors include evidence where available.
- [ ] Recommended action is clearly shown.
- [ ] Sensitive information is minimized.
- [ ] Critical actions require appropriate confirmation.

### Dependencies
ARM-019, ARM-020

---

## ARM-022 — Implement Analyst Decision APIs

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement approve, review, and block transaction decision endpoints. Persist the analyst decision, user, reason, timestamp, previous recommendation, and resulting transaction status. Enforce authorization server-side.

### Acceptance Criteria
- [ ] Only authorized roles can perform permitted actions.
- [ ] Approve/Review/Block persist successfully.
- [ ] Manual override reason is captured where required.
- [ ] Duplicate/conflicting decisions are handled safely.
- [ ] Every decision creates an auditable record.
- [ ] The response reflects the confirmed backend status.

### Dependencies
ARM-014, ARM-004, ARM-003

---

## ARM-023 — Build Decision Workflow UI

**Priority:** `must-have for launch`

### AI Coding Prompt
Implement Approve, Review, and Block actions in the investigation UI with confirmation, reason capture where required, loading prevention for duplicate submissions, and post-action refresh.

### Acceptance Criteria
- [ ] Buttons match the user's permissions.
- [ ] Block and other consequential actions use confirmation.
- [ ] Reason is validated where required.
- [ ] Double submission is prevented.
- [ ] UI does not show a final decision until backend confirmation.
- [ ] Decision history updates after success.

### Dependencies
ARM-021, ARM-022

---

## ARM-024 — Implement Alerts Generation

**Priority:** `must-have for launch`

### AI Coding Prompt
Generate persistent alerts for high-risk transactions, unusual transaction spikes, repeated suspicious activity, and other MVP risk conditions supported by stored data. Avoid duplicate alert storms.

### Acceptance Criteria
- [ ] High-risk transaction alerts are generated when configured.
- [ ] Spike/unusual activity alerts can be generated from defined thresholds.
- [ ] Duplicate events do not create uncontrolled duplicate alerts.
- [ ] Alerts are merchant-scoped.
- [ ] Alert severity and source are persisted.

### Dependencies
ARM-014, ARM-003

---

## ARM-025 — Build Alerts API

**Priority:** `must-have for launch`

### AI Coding Prompt
Create paginated alert APIs with severity/status filters and an endpoint to mark alerts as read. Return links to relevant transactions where applicable.

### Acceptance Criteria
- [ ] Alerts can be listed with pagination.
- [ ] Severity/status filtering works.
- [ ] Read/unread state can be updated by authorized users.
- [ ] Transaction references resolve safely.
- [ ] Errors use the standard API error contract.

### Dependencies
ARM-024, ARM-004

---

## ARM-026 — Build Alerts UI

**Priority:** `must-have for launch`

### AI Coding Prompt
Create an alerts page and top-bar notification experience showing severity, message, timestamp, read state, and related transaction. Use persistent alerts for important operational events.

### Acceptance Criteria
- [ ] Unread alerts are visibly distinguishable without color alone.
- [ ] Users can mark alerts read.
- [ ] Relevant alerts link to investigation pages.
- [ ] Loading, empty, and error states exist.
- [ ] Critical information is not communicated only through temporary toasts.

### Dependencies
ARM-015, ARM-025

---

## ARM-027 — Build Risk Rules Management API

**Priority:** `nice-to-have`

### AI Coding Prompt
Create CRUD APIs for configurable merchant risk rules covering field, operator, value, action, enabled status, and audit metadata. Prevent arbitrary code execution or unsafe rule definitions.

### Acceptance Criteria
- [ ] Authorized users can list rules.
- [ ] Authorized users can create/update/disable supported rule types.
- [ ] Invalid rule definitions are rejected.
- [ ] Rule changes are versioned/audited.
- [ ] Rule evaluation uses only supported safe operators.

### Dependencies
ARM-011, ARM-004, ARM-003

---

## ARM-028 — Build Risk Rules UI

**Priority:** `nice-to-have`

### AI Coding Prompt
Create a rule management screen and controlled rule builder for amount, failed attempts, velocity, new device, and supported conditions. Allow safe enable/disable and confirmation for impactful changes.

### Acceptance Criteria
- [ ] Users can view configured rules.
- [ ] Authorized admins can create/edit/disable supported rules.
- [ ] Form validation prevents invalid combinations.
- [ ] Changes show clear success/error feedback.
- [ ] Rules cannot execute arbitrary user code.

### Dependencies
ARM-027, ARM-015

---

## ARM-029 — Build Historical Analytics API

**Priority:** `nice-to-have`

### AI Coding Prompt
Create analytics endpoints for transaction volume, fraud/high-risk trends, block/review rates, average risk score, and risk by payment method over selectable periods.

### Acceptance Criteria
- [ ] Analytics are merchant-scoped.
- [ ] Period filters return consistent time-series data.
- [ ] Metrics are derived from authoritative stored records.
- [ ] Insufficient data is represented safely.
- [ ] Queries remain performant with indexed data.

### Dependencies
ARM-003, ARM-014

---

## ARM-030 — Build Analytics Dashboard UI

**Priority:** `nice-to-have`

### AI Coding Prompt
Create historical analytics visualizations using the approved charting library. Include risk trend, volume, risk distribution, block/review rates, and payment-method breakdown where available.

### Acceptance Criteria
- [ ] Charts render from backend data.
- [ ] Time period can be changed.
- [ ] Charts have accessible labels/legends.
- [ ] Empty and error states exist.
- [ ] Charts do not imply causation beyond the available data.

### Dependencies
ARM-029, ARM-015

---

## ARM-031 — Implement Analyst Feedback Capture

**Priority:** `nice-to-have`

### AI Coding Prompt
Capture cases where analyst decisions differ from AI recommendations and where later outcomes indicate fraud/non-fraud. Store feedback as labeled decision data without automatically retraining production models.

### Acceptance Criteria
- [ ] Override decisions are linked to the original assessment.
- [ ] Feedback includes decision timestamp and actor.
- [ ] Feedback can be exported/queried for future training.
- [ ] No automatic production retraining occurs in this ticket.
- [ ] Feedback cannot alter historical decisions.

### Dependencies
ARM-022, ARM-014, ARM-003

---

## ARM-032 — Build Model Performance API

**Priority:** `nice-to-have`

### AI Coding Prompt
Expose model evaluation metrics and version information for risk operations users. Include precision, recall, F1, ROC-AUC, PR-AUC, false-positive and false-negative rates when labels are available.

### Acceptance Criteria
- [ ] Metrics are tied to a model version and evaluation dataset/time period.
- [ ] Metrics are clearly distinguished from live transaction KPIs.
- [ ] Only authorized roles can access model performance information.
- [ ] Missing labels do not produce fabricated metrics.

### Dependencies
ARM-009, ARM-003, ARM-004

---

## ARM-033 — Build Model Performance UI

**Priority:** `nice-to-have`

### AI Coding Prompt
Create a model monitoring view showing model version, evaluation metrics, threshold information, and recent performance trends when sufficient labeled data exists.

### Acceptance Criteria
- [ ] Model version is visible.
- [ ] Metrics are clearly labeled.
- [ ] No metric is shown without sufficient supporting data.
- [ ] Role restrictions are respected.
- [ ] The UI distinguishes offline evaluation from live production performance.

### Dependencies
ARM-032, ARM-015

---

## ARM-034 — Add Payment Provider Webhook Boundary

**Priority:** `should-have`

### AI Coding Prompt
Create a secure backend webhook boundary for supported payment-provider events. Verify signatures using provider-specific server-side credentials, validate event structure, persist an idempotent event record, and pass valid transaction events into the risk workflow.

### Acceptance Criteria
- [ ] Webhook endpoint is server-side only.
- [ ] Provider signature verification is implemented according to the selected provider's official documentation.
- [ ] Duplicate events are idempotent.
- [ ] Invalid signatures are rejected.
- [ ] Webhook secrets are never exposed to the frontend.
- [ ] Accepted events can create/update the internal transaction record.

### Dependencies
ARM-006, ARM-007, ARM-014

---

## ARM-035 — Add Razorpay Integration Adapter

**Priority:** `should-have`

### AI Coding Prompt
If the Razorpay track requires live Razorpay data, implement a backend-only Razorpay adapter behind an internal service interface. Keep provider credentials server-side and map provider data into the canonical transaction schema. If live access is unavailable, provide a mock adapter for the demo rather than inventing credentials or undocumented endpoints.

### Acceptance Criteria
- [ ] Provider credentials exist only on the backend.
- [ ] Provider payloads are normalized into the internal transaction schema.
- [ ] Provider errors are translated into safe internal errors.
- [ ] Integration can be disabled/configured without changing frontend code.
- [ ] Mock mode can demonstrate the complete workflow when live credentials are unavailable.

### Dependencies
ARM-006, ARM-007, ARM-034

---

## ARM-036 — Implement Comprehensive Frontend States

**Priority:** `must-have for launch`

### AI Coding Prompt
Complete all core frontend pages with loading skeletons, empty states, validation errors, permission errors, network failures, service-unavailable states, 404s, and safe retry behavior.

### Acceptance Criteria
- [ ] Every core screen has loading, success, empty, and error states.
- [ ] 401 redirects/re-authentication behavior works.
- [ ] 403 does not reveal unauthorized data.
- [ ] 500/503 show safe messages and request IDs when available.
- [ ] Retries do not duplicate destructive actions.

### Dependencies
ARM-017, ARM-019, ARM-021, ARM-023, ARM-026

---

## ARM-037 — Implement Audit Logging

**Priority:** `must-have for launch`

### AI Coding Prompt
Persist auditable records for authentication-sensitive actions, risk decisions, rule changes, and other high-impact operations. Provide a backend-safe audit model that cannot be edited through ordinary application workflows.

### Acceptance Criteria
- [ ] High-impact actions create audit entries.
- [ ] Entries include actor, action, resource, timestamp, and result.
- [ ] Analyst decisions include reason when applicable.
- [ ] Audit data is merchant-scoped.
- [ ] Ordinary users cannot modify audit records.

### Dependencies
ARM-022, ARM-004, ARM-027

---

## ARM-038 — Implement Database Row-Level Security / Tenant Isolation

**Priority:** `must-have for launch`

### AI Coding Prompt
Enforce merchant/tenant isolation at the database and service layers. Apply row-level security or equivalent database policies to transaction, customer, risk, alert, rule, and decision data so one merchant cannot access another merchant's records.

### Acceptance Criteria
- [ ] Cross-merchant reads are blocked.
- [ ] Cross-merchant writes are blocked.
- [ ] Policies are tested with multiple merchant contexts.
- [ ] Backend authorization remains enabled in addition to database isolation.
- [ ] Service/admin database paths are explicitly controlled and audited.

### Dependencies
ARM-003, ARM-004

---

## ARM-039 — Add Security and Input Hardening

**Priority:** `must-have for launch`

### AI Coding Prompt
Harden the application against common web/API threats: injection, unsafe rendering, oversized payloads, abusive requests, insecure CORS, leaked secrets, and unsafe logging. Apply secure headers and data minimization.

### Acceptance Criteria
- [ ] No secrets are present in frontend bundles.
- [ ] Input validation exists at API boundaries.
- [ ] Sensitive values are excluded from logs.
- [ ] CORS is restricted to approved origins.
- [ ] Rate limiting or equivalent abuse protection is configured for sensitive endpoints.
- [ ] Unsafe HTML rendering is avoided.
- [ ] Security headers are configured for production.

### Dependencies
ARM-002, ARM-004, ARM-005

---

## ARM-040 — Add Observability and Request Correlation

**Priority:** `should-have`

### AI Coding Prompt
Add structured backend logging, request IDs, latency measurement, and frontend error monitoring hooks. Ensure logs do not contain passwords, tokens, card security codes, or unnecessary sensitive payment data.

### Acceptance Criteria
- [ ] Each API request has a correlation/request ID.
- [ ] Errors can be traced from UI message to backend logs.
- [ ] Risk inference latency is measurable.
- [ ] Sensitive fields are redacted.
- [ ] Production monitoring can distinguish application errors from expected validation errors.

### Dependencies
ARM-002, ARM-005

---

## ARM-041 — Performance and Scalability Hardening

**Priority:** `should-have`

### AI Coding Prompt
Optimize the MVP for the target risk decision latency and dashboard responsiveness. Add appropriate database indexes, server-side pagination, query optimization, frontend code splitting, and controlled polling where required.

### Acceptance Criteria
- [ ] Risk decision target is measured and documented.
- [ ] Transaction lists do not load unbounded records.
- [ ] Common dashboard queries use appropriate indexes.
- [ ] Frontend pages are lazy-loaded where beneficial.
- [ ] Polling is bounded and disabled when unnecessary.
- [ ] Performance regressions can be detected through basic measurements.

### Dependencies
ARM-014, ARM-017, ARM-018

---

## ARM-042 — Automated Test Suite

**Priority:** `must-have for launch`

### AI Coding Prompt
Build automated tests for core backend risk scoring, rule evaluation, API authorization, tenant isolation, transaction decisions, and critical frontend workflows. Include representative fraud and legitimate transaction cases.

### Acceptance Criteria
- [ ] Core scoring has deterministic unit tests.
- [ ] Rule engine tests cover triggered and non-triggered rules.
- [ ] API authorization tests cover allowed and denied roles.
- [ ] Cross-merchant isolation tests pass.
- [ ] Approve/Review/Block workflows are tested.
- [ ] Critical frontend flows have automated coverage.
- [ ] Tests run from a clean environment.

### Dependencies
ARM-014, ARM-023, ARM-038

---

## ARM-043 — Seed Demo Dataset and Demo Mode

**Priority:** `must-have for launch`

### AI Coding Prompt
Create a safe, synthetic demo dataset containing legitimate, suspicious, and high-risk transactions that demonstrates the complete product workflow. Add a controlled demo mode for the Razorpay track when live payment data is unavailable.

### Acceptance Criteria
- [ ] Dataset contains representative Low/Medium/High cases.
- [ ] Synthetic records contain no real customer/payment secrets.
- [ ] Dashboard and investigation screens work with seeded data.
- [ ] Risk explanations are populated.
- [ ] Demo setup is reproducible with one documented command/process.

### Dependencies
ARM-014, ARM-017, ARM-021

---

## ARM-044 — Production Deployment Configuration

**Priority:** `must-have for launch`

### AI Coding Prompt
Prepare deployment configuration for the React frontend, FastAPI backend, PostgreSQL database, ML artifact, environment variables, migrations, health checks, and secure production settings.

### Acceptance Criteria
- [ ] Frontend and backend can be deployed separately or through the documented deployment setup.
- [ ] Production environment variables are documented.
- [ ] Database migrations run successfully.
- [ ] Health checks work.
- [ ] HTTPS is assumed/enforced at deployment.
- [ ] Secrets are provided through the deployment secret manager/environment, not source control.

### Dependencies
ARM-039, ARM-041, ARM-042

---

## ARM-045 — End-to-End MVP Acceptance Test

**Priority:** `must-have for launch`

### AI Coding Prompt
Run a complete end-to-end test from transaction ingestion through feature extraction, ML + rules evaluation, risk score, explanation, dashboard display, alert generation, analyst investigation, decision, and audit record.

### Acceptance Criteria
- [ ] A synthetic high-risk transaction completes the entire workflow.
- [ ] Risk score, level, reasons, and recommendation are consistent across API and UI.
- [ ] Alert is generated and linked to the transaction.
- [ ] Analyst can make an authorized decision.
- [ ] Decision and audit record are persisted.
- [ ] No unauthorized data is exposed.
- [ ] The documented MVP success criteria can be demonstrated.

### Dependencies
ARM-043, ARM-044, ARM-042, ARM-037

---

# Ticket Summary

| Priority | Count |
|---|---:|
| must-have for launch | 34 |
| should-have | 4 |
| nice-to-have | 7 |

# MVP Critical Path

```text
Foundation
  ARM-001 + ARM-002
        ↓
  ARM-003 + ARM-004 + ARM-005
        ↓
Transaction Schema / Ingestion
  ARM-006 → ARM-007 → ARM-008
        ↓
Risk Engine
  ARM-009 + ARM-010
        +
  ARM-011
        ↓
  ARM-012 → ARM-013 → ARM-014
        ↓
Core Product
  ARM-015 → ARM-016 → ARM-017
  ARM-018 → ARM-019 → ARM-020 → ARM-021
        ↓
Decision / Alert Workflow
  ARM-022 → ARM-023
  ARM-024 → ARM-025 → ARM-026
        ↓
Security / Quality
  ARM-036 + ARM-037 + ARM-038 + ARM-039
  ARM-040 + ARM-041 + ARM-042
        ↓
Demo / Deployment / Acceptance
  ARM-043 → ARM-044 → ARM-045
```

# PRD Alignment

The tickets directly cover the PRD's core loop:

**Transaction → Feature Extraction → Rule Checks → ML Risk Model → Risk Score → Explanation → Decision → Dashboard/Alert → Analyst Feedback**

The list deliberately keeps graph-based fraud detection, autonomous investigation agents, mobile apps, full payment-gateway functionality, global cross-merchant intelligence, and autonomous production model retraining outside the V1 critical path, consistent with the supplied PRD's non-goals.

## Source
The ticket breakdown is based on the uploaded Product Requirements Document — AI Risk Manager. fileciteturn0file0