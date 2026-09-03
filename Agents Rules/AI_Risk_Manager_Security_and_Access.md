# Security & Access Document — AI Risk Manager

**Product:** AI Risk Manager — Razorpay Track  
**Document Type:** Security and Access Document  
**Version:** MVP / Version 1.0  
**Audience:** Product team, developers, founders, reviewers  
**Primary Goal:** Protect the AI Risk Manager platform, transaction data, user accounts, risk decisions, and audit trail while keeping the MVP practical to build.

---

# 1. Executive Summary

AI Risk Manager is a payment-risk decisioning platform. It receives transaction information, evaluates risk using rules and machine learning, produces a risk score, explains the decision, and recommends:

- **APPROVE**
- **REVIEW**
- **BLOCK**

Because the application deals with payment-related information and fraud decisions, security cannot be treated as a feature added at the end.

The MVP should follow five principles:

1. **Least privilege** — users only receive the access they actually need.
2. **Defense in depth** — never depend on one security control.
3. **Fail safely** — errors should not accidentally approve or expose sensitive transactions.
4. **Audit everything important** — security-sensitive actions must be traceable.
5. **Minimize sensitive data** — never store payment credentials that the product does not need.

For V1, use a **JWT-based authentication system with short-lived access tokens, secure password hashing, role-based authorization, PostgreSQL row-level security where appropriate, strict API validation, centralized error handling, and comprehensive audit logging.**

---

# 2. Security Goals

The security architecture must protect:

### Confidentiality

Users should only see data belonging to their merchant organization and authorized records.

### Integrity

Users must not be able to silently alter:

- Transactions
- Risk assessments
- AI decisions
- Audit logs
- Other users' permissions

### Availability

The risk engine should remain available and fail predictably when a dependency is unavailable.

### Accountability

Important actions must be recorded so the system can answer:

> Who did what, when, and to which transaction?

### Privacy

Only information necessary for risk analysis should be stored.

---

# 3. Recommended Authentication

## Recommendation: JWT Authentication

For the MVP, use:

**Email + password + JWT access tokens**

This is a good balance between security, implementation effort, and scalability.

### Login Flow

```text
User
  ↓
Email + Password
  ↓
FastAPI
  ↓
Verify Password Hash
  ↓
Create Short-Lived JWT
  ↓
Return Access Token
  ↓
Frontend
  ↓
Authenticated API Requests
```

---

# 4. Password Security

Never store passwords directly.

Bad:

```text
password = "mypassword123"
```

Correct:

```text
password_hash = "<secure hash>"
```

Use a modern password hashing library and a strong password hashing algorithm.

### Password requirements

Require:

- Minimum length
- Reasonable complexity
- Protection against obviously weak passwords
- Rate limiting on repeated login failures

Do not impose unnecessarily complicated rules that encourage users to write passwords down.

---

# 5. JWT Security

JWTs should contain only the information required to identify the authenticated session.

Example claims:

```json
{
  "sub": "user_uuid",
  "merchant_id": "merchant_uuid",
  "role": "ANALYST",
  "exp": 1770000000
}
```

### Recommended controls

- Short access-token lifetime
- Strong random signing secret
- Token expiration
- Token validation on every protected request
- Never place passwords or sensitive payment information in JWTs
- Rotate secrets if compromise is suspected

For a browser-based production deployment, prefer secure, appropriately configured cookies for token/session handling rather than exposing long-lived credentials to client-side JavaScript.

---

# 6. Authentication vs Authorization

These are different.

### Authentication

Answers:

> **Who are you?**

Example:

```text
Satyam → authenticated user
```

### Authorization

Answers:

> **What are you allowed to do?**

Example:

```text
Analyst → can investigate transactions
Admin → can manage users and risk rules
```

A valid login must never automatically mean full access.

---

# 7. User Roles

The MVP should have two main roles:

```text
ADMIN
ANALYST
```

A future system can introduce additional roles such as:

```text
VIEWER
RISK_MANAGER
SUPER_ADMIN
```

but they are unnecessary for V1.

---

# 8. ADMIN Role

The Admin is responsible for merchant-level configuration and team management.

## Admin CAN

### Account Management

- View merchant account
- Update merchant settings
- Manage users
- Create analysts
- Disable users
- Reset user access through approved flows

### Risk Management

- View all merchant transactions
- View all risk assessments
- Configure risk thresholds
- Create risk rules
- Update risk rules
- Enable/disable risk rules

### Investigation

- View suspicious transactions
- Review risk explanations
- Approve transactions
- Block transactions
- Override AI recommendations

### Analytics

- View risk analytics
- View fraud trends
- View transaction trends
- View model performance metrics available to the product

### Security

- View audit logs
- Review important account activity

---

# 9. ADMIN Role — What They CANNOT Do

Even an Admin should not be able to:

- View raw card numbers
- View CVV
- Recover plaintext passwords
- Modify historical audit-log entries
- Change another merchant's data
- Directly manipulate database records through the application
- Disable security logging
- Bypass authentication
- Alter a completed transaction's original raw event without creating an auditable correction

The Admin has broad application permissions, but not unrestricted access to sensitive infrastructure.

---

# 10. ANALYST Role

The Analyst is focused on transaction investigation.

## Analyst CAN

### Transactions

- View transactions belonging to their merchant
- Search transactions
- Filter transactions
- Open transaction details
- View risk scores
- View risk factors
- View model explanations

### Investigation

- Approve a transaction
- Block a transaction
- Mark a transaction for review
- Add an investigation reason
- View relevant transaction history

### Alerts

- View alerts
- Mark alerts as read
- Investigate alert-related transactions

### Analytics

- View approved analytics dashboards relevant to their role

---

# 11. ANALYST Role — What They CANNOT Do

Analysts should NOT be able to:

- Create or delete users
- Change user roles
- Change merchant configuration
- Modify risk thresholds
- Create or modify global risk rules
- Disable security controls
- Delete transactions
- Delete risk assessments
- Delete audit logs
- Access another merchant's data
- Change ML model files
- Change application secrets

This separation protects the system from accidental or malicious privilege escalation.

---

# 12. Permission Matrix

| Capability | ADMIN | ANALYST |
|---|---:|---:|
| Login | ✅ | ✅ |
| View dashboard | ✅ | ✅ |
| View transactions | ✅ | ✅ |
| View transaction details | ✅ | ✅ |
| View risk score | ✅ | ✅ |
| View risk explanations | ✅ | ✅ |
| Approve transaction | ✅ | ✅ |
| Block transaction | ✅ | ✅ |
| Add investigation reason | ✅ | ✅ |
| View alerts | ✅ | ✅ |
| Mark alerts read | ✅ | ✅ |
| View analytics | ✅ | ✅ |
| Create users | ✅ | ❌ |
| Disable users | ✅ | ❌ |
| Change user roles | ✅ | ❌ |
| Create risk rules | ✅ | ❌ |
| Edit risk rules | ✅ | ❌ |
| Delete risk rules | ✅ | ❌ |
| Change risk thresholds | ✅ | ❌ |
| View audit logs | ✅ | ❌ |
| Change model | ❌* | ❌ |
| Access database directly | ❌ | ❌ |
| View raw card data | ❌ | ❌ |

\* Model deployment should be an engineering/deployment responsibility, not an application-user permission.

---

# 13. Merchant Isolation

The most important authorization rule is:

> **A user must never be able to access another merchant's data.**

Example:

```text
Merchant A
 ├── User A1
 ├── User A2
 └── Transactions A

Merchant B
 ├── User B1
 ├── User B2
 └── Transactions B
```

User A1 must never receive:

```text
Merchant B transactions
Merchant B customers
Merchant B alerts
Merchant B rules
Merchant B analytics
```

even if they manually modify an API request.

---

# 14. Row-Level Security

PostgreSQL Row-Level Security (RLS) should be used as an additional database-level protection layer.

The application should still perform authorization checks. RLS is defense in depth, not a replacement for application authorization.

---

# 15. RLS Principle

Every merchant-owned table should contain:

```text
merchant_id
```

Examples:

```text
users
customers
transactions
risk_rules
alerts
```

The database should allow access only when:

```text
row.merchant_id = authenticated_user.merchant_id
```

---

# 16. Transactions RLS

Conceptually:

```text
User belongs to Merchant A

Request:
GET /transactions

Database:
Return only rows where
transaction.merchant_id = Merchant A
```

If a malicious user attempts:

```text
GET /transactions/{merchant_B_transaction_id}
```

the query should return:

```text
NOT FOUND
```

or an equivalent access-safe response.

Do not reveal:

> "This transaction exists but belongs to another merchant."

That can leak information.

---

# 17. Customers RLS

Users may access only:

```text
customers.merchant_id = current_user.merchant_id
```

They must not be able to:

- Read another merchant's customers
- Modify another merchant's customers
- Delete another merchant's customers

---

# 18. Risk Rules RLS

Risk rules belong to a merchant.

Therefore:

```text
merchant_id = current_user.merchant_id
```

An Analyst can read rules if the product requires it, but only an Admin can create or modify them.

---

# 19. Alerts RLS

Alerts must be restricted by merchant:

```text
alert.merchant_id = current_user.merchant_id
```

An Analyst can view alerts.

An Admin can view and manage them.

---

# 20. Risk Assessments RLS

Risk assessments are connected to transactions.

The effective rule is:

```text
risk_assessment
    ↓
transaction
    ↓
merchant_id
    ↓
current_user.merchant_id
```

A user cannot access a risk assessment simply by knowing its UUID.

---

# 21. Analyst Decisions RLS

Analyst decisions should be accessible only within the relevant merchant.

Additionally:

```text
analyst_id = authenticated_user.id
```

can be used where the product needs to restrict analysts from editing or managing another analyst's workflow records.

Historical decisions should be immutable.

---

# 22. Audit Logs

Audit logs are security-sensitive.

Normal users should not be able to modify them.

Recommended policy:

```text
Application Users
      ↓
INSERT audit event
      ↓
Audit Storage

No user
      ↓
UPDATE/DELETE audit event
```

Even Admins should not be able to delete audit history from the application.

---

# 23. Database Access Rules

Application users should never connect directly to PostgreSQL.

Use:

```text
Frontend
   ↓
FastAPI
   ↓
Authorization
   ↓
SQLAlchemy
   ↓
PostgreSQL
```

Never:

```text
Frontend
   ↓
PostgreSQL
```

---

# 24. API Security

Every protected API endpoint should perform:

```text
1. Authenticate user
2. Identify merchant
3. Check role
4. Validate request
5. Perform merchant ownership check
6. Execute operation
7. Record important action
```

Example:

```text
GET /api/v1/transactions/123

        ↓
JWT valid?
        ↓
YES
        ↓
Which merchant?
        ↓
Does transaction belong to merchant?
        ↓
YES
        ↓
Does user have permission?
        ↓
YES
        ↓
Return transaction
```

---

# 25. Input Validation

Never trust client input.

Validate:

- UUIDs
- Amounts
- Currency
- Payment methods
- Transaction status
- Risk thresholds
- Rule conditions
- Pagination
- Sorting fields
- Date ranges

Reject malformed input before it reaches business logic.

---

# 26. SQL Injection Protection

Do not build SQL queries by concatenating strings.

Bad:

```python
query = "SELECT * FROM transactions WHERE id = '" + transaction_id + "'"
```

Use SQLAlchemy's parameterized queries instead.

This prevents attackers from injecting SQL commands.

---

# 27. API Rate Limiting

Rate limiting should be applied particularly to:

- Login
- Registration
- Password-reset flows
- Risk evaluation endpoints
- Expensive analytics endpoints

Example:

```text
Too many login attempts
        ↓
Temporarily slow/reject requests
```

This reduces brute-force and abuse attempts.

---

# 28. CORS

Only allow trusted frontend origins.

Development:

```text
http://localhost:5173
```

Production:

```text
https://your-approved-domain.example
```

Do not use:

```text
allow_origins=["*"]
```

for a production authenticated application.

---

# 29. Error Handling Philosophy

The system should follow:

> **Fail safely, fail clearly, and never leak sensitive information.**

A user should receive a useful error message.

A developer should receive enough diagnostic information in secure logs.

An attacker should receive as little internal information as possible.

---

# 30. Standard API Error Format

Use a consistent structure.

Example:

```json
{
  "success": false,
  "error": {
    "code": "TRANSACTION_NOT_FOUND",
    "message": "The requested transaction could not be found.",
    "request_id": "req_123"
  }
}
```

The `request_id` helps developers trace the request in logs.

---

# 31. Authentication Errors

## Invalid Login

User sees:

```text
Invalid email or password.
```

Do NOT reveal:

```text
Email exists but password is incorrect.
```

That can help attackers discover valid accounts.

### HTTP

```text
401 Unauthorized
```

---

# 32. Expired Token

When a token expires:

```text
401 Unauthorized
```

Frontend should:

1. Clear invalid authentication state.
2. Redirect user to login.
3. Ask them to authenticate again.

Do not expose JWT internals.

---

# 33. Insufficient Permission

Example:

Analyst tries to modify a risk rule.

Return:

```text
403 Forbidden
```

Message:

```text
You do not have permission to perform this action.
```

Do not reveal unnecessary internal authorization details.

---

# 34. Cross-Merchant Access Attempt

If User A requests Merchant B's transaction:

Return:

```text
404 Not Found
```

where appropriate.

This prevents exposing whether the resource exists.

Record the suspicious access attempt in security logs.

---

# 35. Invalid Request

Example:

```text
amount = "hello"
```

Return:

```text
400 Bad Request
```

with a clear validation message.

Example:

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Transaction amount must be a valid positive number."
  }
}
```

---

# 36. Transaction Risk Engine Failure

This is one of the most important failure cases.

Suppose:

```text
Transaction
    ↓
Risk Engine
    ↓
ML model crashes
```

Do NOT silently approve the transaction.

The safe behavior depends on the surrounding payment architecture.

For this standalone MVP:

```text
Risk evaluation failed
        ↓
Mark evaluation as FAILED
        ↓
Do not present a false risk score
        ↓
Require retry/manual review
```

Example status:

```text
RISK_EVALUATION_FAILED
```

If integrated into an actual payment authorization flow, the fail-open/fail-closed decision must be explicitly defined with the payment/risk owner because either choice has business consequences.

---

# 37. ML Model Unavailable

If the ML model cannot load:

```text
ML service unavailable
```

The system should not fabricate a prediction.

Possible MVP behavior:

```text
ML unavailable
      ↓
Run deterministic safety rules
      ↓
If rules identify high risk
      → REVIEW/BLOCK according to configured policy
      ↓
Otherwise
      → REVIEW rather than pretending ML approved it
```

The UI should clearly show:

```text
AI assessment unavailable.
Manual review recommended.
```

---

# 38. Database Failure

If PostgreSQL becomes unavailable:

```text
API
 ↓
Database unavailable
```

Return:

```text
503 Service Unavailable
```

Do not expose:

```text
PostgreSQL connection refused
database password
hostnames
stack traces
```

Log the technical failure internally.

---

# 39. Database Timeout

If a database query exceeds its allowed time:

Return:

```text
503 Service Unavailable
```

or an appropriate timeout response.

Internally record:

- Request ID
- Endpoint
- Query category
- Duration
- Error type

Do not log sensitive transaction contents.

---

# 40. External Service Failure

If a future external service such as IP reputation becomes unavailable:

```text
External service
      ↓
Unavailable
```

The system should:

1. Record the dependency failure.
2. Mark that signal as unavailable.
3. Continue using available signals if the decision remains safe.
4. Avoid treating "unknown" as "safe."
5. Apply a conservative fallback policy.

---

# 41. Duplicate Transaction

Payment systems can retry requests.

Therefore:

```text
Same external_transaction_id
        ↓
Received twice
```

must not create two independent transaction records.

Use an idempotency mechanism.

Example:

```text
external_transaction_id
```

should have an appropriate unique constraint within the merchant context.

---

# 42. Duplicate Risk Evaluation

A transaction may accidentally be evaluated twice.

The system should either:

- Reuse an existing valid assessment, or
- Create a new versioned assessment intentionally.

Never silently overwrite historical risk decisions.

---

# 43. Extremely Large Transaction Amount

Handle:

```text
amount = very large number
```

using strict numeric validation.

Prevent:

- Overflow
- Negative values
- Impossible decimal precision
- Unexpected scientific notation if not supported

Example:

```text
amount <= 0
```

should be rejected.

---

# 44. Negative Transaction Amount

Reject unless the product explicitly supports a transaction type where negative values are meaningful.

For standard payment authorization:

```text
amount <= 0
```

should produce a validation error.

---

# 45. Currency Edge Cases

Validate supported currencies.

For V1, if the system primarily supports INR:

```text
currency = INR
```

should be accepted.

Unknown currencies should be rejected rather than silently converted.

---

# 46. Future-Dated Transactions

A transaction timestamp significantly in the future may indicate:

- Client clock problems
- Data corruption
- Replay attempts
- Malicious input

Validate timestamp ranges.

Do not blindly trust client-provided time.

---

# 47. Very Old Transactions

Historical imports may contain old timestamps.

Define an explicit policy:

```text
Real-time API
→ only accepts transactions within allowed time window

Historical import
→ separate ingestion process
```

Do not mix the two workflows without validation.

---

# 48. Missing Customer

A transaction may arrive without a known customer.

Do not crash.

Possible behavior:

```text
Customer unavailable
      ↓
Use transaction-level signals
      ↓
Increase uncertainty
      ↓
Potential REVIEW
```

The UI should say:

```text
Limited customer history available.
```

---

# 49. New Customer

A new customer is not automatically fraudulent.

Correct behavior:

```text
New customer
      +
Large transaction
      +
New device
      +
High velocity
      ↓
Higher risk
```

Avoid:

```text
New customer = Fraud
```

This reduces false positives.

---

# 50. New Device

A new device should be treated as a risk signal, not proof of fraud.

Example:

```text
New device
+
Normal amount
+
Normal behavior
+
Known customer
```

may remain low risk.

---

# 51. High Transaction Velocity

Example:

```text
25 transactions
within 2 minutes
```

should trigger a velocity rule.

However, legitimate businesses may have high-volume periods.

Therefore the rule should be configurable.

---

# 52. Multiple Accounts on One Device

Example:

```text
Device X
 ↓
Account A
Account B
Account C
Account D
Account E
```

This may be suspicious.

But shared devices can be legitimate.

Use it as a contributing factor, not an automatic fraud verdict.

---

# 53. IP Address Issues

IP addresses can be:

- Missing
- Shared
- Proxied
- VPN-based
- IPv4
- IPv6

Never treat:

```text
VPN = Fraud
```

Instead:

```text
VPN / unusual IP
+
other suspicious signals
=
higher risk
```

---

# 54. Model Output Outside Expected Range

The ML model should produce a validated probability.

Expected:

```text
0.0 <= probability <= 1.0
```

If output is outside that range or is:

```text
NaN
Infinity
null
```

mark the ML result invalid.

Never convert invalid output into a valid-looking risk score.

---

# 55. Risk Score Validation

Risk score must remain:

```text
0–100
```

If internal calculations produce:

```text
-20
```

or:

```text
150
```

clamp or reject according to the defined risk-engine contract.

Never send invalid scores to the frontend.

---

# 56. Explainability Failure

If the model generates a risk score but explanation generation fails:

Do not invent an explanation.

UI should display:

```text
Risk score generated.
Detailed explanation is temporarily unavailable.
```

If explainability is a required safety condition for the product decision, route the transaction to manual review instead.

---

# 57. Rule Engine Failure

If configured rules cannot be evaluated:

```text
Rule evaluation failed
```

The system should:

1. Record the failure.
2. Avoid pretending all rules passed.
3. Apply a defined fallback policy.
4. Consider manual review for affected transactions.

---

# 58. Risk Threshold Misconfiguration

Admin may accidentally configure:

```text
low threshold = 90
high threshold = 20
```

This should be rejected.

Valid configuration must satisfy:

```text
0 <= low_threshold < high_threshold <= 100
```

---

# 59. Rule Configuration Security

Never allow arbitrary executable code in risk rules.

Avoid rules like:

```text
execute_python(...)
```

or arbitrary expressions from users.

Use a controlled structure:

```json
{
  "field": "failed_attempts",
  "operator": ">",
  "value": 5
}
```

Only allow approved:

- Fields
- Operators
- Values
- Actions

This prevents rule injection.

---

# 60. File Upload Security

If future versions allow CSV uploads:

Validate:

- File extension
- MIME type
- File size
- Number of rows
- Column names
- Data types
- Malicious content

Do not execute uploaded files.

For MVP, keep imports restricted to trusted CSV structures.

---

# 61. Logging Rules

Logs should contain enough information to investigate problems but never expose sensitive data.

### Safe to log

```text
request_id
user_id
merchant_id
endpoint
HTTP status
latency
error code
model version
rule ID
```

### Do NOT log

```text
password
password_hash
JWT token
CVV
raw card number
secret API keys
database passwords
```

---

# 62. Audit Events

Record events such as:

```text
USER_LOGIN
USER_LOGIN_FAILED
USER_CREATED
USER_DISABLED
ROLE_CHANGED
TRANSACTION_VIEWED
TRANSACTION_REVIEWED
TRANSACTION_APPROVED
TRANSACTION_BLOCKED
RISK_RULE_CREATED
RISK_RULE_UPDATED
RISK_RULE_DISABLED
SETTINGS_CHANGED
SECURITY_VIOLATION
```

---

# 63. Audit Log Integrity

Audit logs should be append-only from the application's perspective.

Users should not be able to:

```text
UPDATE audit_log
DELETE audit_log
```

The purpose is to preserve trustworthy history.

---

# 64. Session Security

Recommended:

- Short-lived access tokens
- Secure session handling
- Logout support
- Token expiration
- Re-authentication for sensitive account changes
- Rate-limited login attempts

For production, consider a dedicated identity provider if the product grows beyond the MVP.

---

# 65. Password Reset

If password reset is implemented:

```text
User requests reset
      ↓
Generate random short-lived reset token
      ↓
Send reset link
      ↓
User sets new password
      ↓
Invalidate reset token
```

Never send the existing password to the user.

---

# 66. Account Lockout

Do not permanently lock accounts after a few failures because this can become an attack vector.

Instead use:

```text
Repeated failures
      ↓
Rate limiting
      +
Increasing delay
      +
Security monitoring
```

---

# 67. Sensitive Configuration

Never commit:

```text
.env
```

to Git.

Use:

```text
.env.example
```

with placeholder values.

---

# 68. Security Environment Variables

Example:

```env
APP_ENV=development
DEBUG=false

DATABASE_URL=postgresql://...

JWT_SECRET_KEY=replace_with_long_random_secret
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

CORS_ORIGINS=http://localhost:5173

MODEL_PATH=./ml/models/risk_model.pkl

LOG_LEVEL=INFO

RATE_LIMIT_ENABLED=true
```

For production, secrets should come from a secure secret-management system rather than being hard-coded in deployment files.

---

# 69. Production Security Configuration

Production should use:

```env
APP_ENV=production
DEBUG=false
```

Never expose:

```text
debug tracebacks
database credentials
secret keys
internal server paths
```

to end users.

---

# 70. HTTP Security

Production should use HTTPS.

Recommended controls include:

- TLS
- Secure cookies where applicable
- HttpOnly cookies where applicable
- SameSite protection
- HSTS
- Content Security Policy where appropriate
- X-Content-Type-Options
- Referrer-Policy

The exact headers should be tested against the frontend and deployment environment rather than copied blindly.

---

# 71. CSRF Protection

If authentication uses cookies, protect state-changing requests against CSRF.

If the application uses Authorization headers with a carefully designed token architecture, CSRF exposure differs, but XSS protection remains critical.

Choose one authentication/session pattern and apply its security controls consistently.

---

# 72. XSS Protection

Never render raw user-controlled HTML.

Risk explanations, transaction descriptions, analyst comments, and rule descriptions should be treated as untrusted input.

React's default escaping should be preserved.

Avoid unnecessary use of:

```text
dangerouslySetInnerHTML
```

---

# 73. Frontend Security

The frontend should never contain:

```text
DATABASE_PASSWORD
JWT_SECRET
API_SECRET
PRIVATE_KEY
```

Anything in a browser bundle should be considered public.

---

# 74. Dependency Security

Keep dependencies updated.

Before launch:

```text
npm audit
pip audit
```

and equivalent security checks should be run.

Remove unused dependencies.

Every additional dependency increases the attack surface.

---

# 75. API Documentation Security

FastAPI automatically exposes API documentation.

During development this is useful:

```text
/docs
/redoc
```

For production, decide whether these endpoints should be public.

If exposed, protect sensitive APIs behind authentication and consider restricting documentation access.

---

# 76. Database Security

Use a dedicated database user for the application.

The application database user should have only the permissions it requires.

Avoid running the application as:

```text
postgres superuser
```

in production.

---

# 77. Database Backups

Production databases should have:

- Automated backups
- Tested restoration
- Appropriate retention
- Access controls
- Encryption where supported

A backup that has never been restored successfully should not be considered a proven backup strategy.

---

# 78. Secrets Management

For the MVP:

```text
.env
```

is acceptable for local development.

For production, use a secure secrets manager provided by your hosting/cloud environment.

Never place secrets in:

- GitHub repositories
- Screenshots
- Frontend source
- README files
- Docker images
- Public logs

---

# 79. AI-Specific Security

AI creates additional security concerns.

### Never trust model output blindly.

Validate:

```text
probability
risk score
risk level
recommended action
explanation
```

against a strict schema.

---

# 80. Model File Protection

The model file:

```text
risk_model.pkl
```

should be treated as a trusted application artifact.

Do not allow normal users to upload or replace it.

Only controlled deployment processes should update models.

---

# 81. Model Poisoning Protection

If future versions use analyst decisions as training data:

```text
Analyst feedback
      ↓
Training dataset
```

do not automatically retrain the model from every single decision.

Instead:

```text
Feedback
   ↓
Validation
   ↓
Curated training dataset
   ↓
Model training
   ↓
Evaluation
   ↓
Approval
   ↓
Deployment
```

This prevents malicious or incorrect feedback from silently poisoning the model.

---

# 82. Risk Decision Integrity

Never let the frontend determine:

```text
risk_score
recommended_action
```

The frontend should display backend results.

Bad:

```text
React calculates:
risk_score = 90
```

Correct:

```text
React
  ↓
FastAPI
  ↓
Risk Engine
  ↓
Risk Score
  ↓
React displays result
```

---

# 83. Analyst Override Security

When an analyst overrides AI:

```text
AI:
BLOCK

Analyst:
APPROVE
```

the system must store:

```text
analyst_id
previous_action
final_action
reason
timestamp
```

This prevents invisible changes to risk decisions.

---

# 84. Critical Decision Confirmation

For particularly sensitive actions, consider confirmation:

```text
BLOCK TRANSACTION
       ↓
Confirmation
       ↓
Enter reason
       ↓
Submit
```

This reduces accidental blocking.

For MVP, this is especially useful on the transaction investigation page.

---

# 85. Edge Case: Double-Click

User clicks:

```text
BLOCK
BLOCK
BLOCK
```

three times.

The API should remain idempotent or safely reject duplicate state changes.

The UI should disable the button during submission.

---

# 86. Edge Case: Analyst Session Expires During Action

Scenario:

```text
Analyst opens transaction
      ↓
Session expires
      ↓
Analyst clicks BLOCK
```

Expected:

```text
401 Unauthorized
```

No transaction state should be changed.

---

# 87. Edge Case: Two Analysts Act Simultaneously

Scenario:

```text
Analyst A → APPROVE
Analyst B → BLOCK
```

The system needs concurrency protection.

Use transaction/version checks so the final state is deterministic and auditable.

Example:

```text
Transaction version = 5

Analyst A submits against version 5
Analyst B submits against version 5

Only one update succeeds.
The other receives a conflict response.
```

---

# 88. Edge Case: Transaction Already Finalized

If a transaction is already:

```text
BLOCKED
```

another user should not accidentally change it without an explicit controlled override.

Return an appropriate conflict response:

```text
409 Conflict
```

---

# 89. Edge Case: Deleted User

If an analyst is disabled:

- They cannot log in.
- Existing audit history remains.
- Historical analyst decisions remain associated with the original user.
- Their past actions must not disappear.

Never cascade-delete important audit history simply because a user account is disabled.

---

# 90. Edge Case: Deleted Customer

For transaction systems, avoid physically deleting customers if transactions depend on their history.

Prefer controlled anonymization or soft deletion where appropriate.

Historical risk decisions should remain understandable.

---

# 91. Edge Case: Database Record Missing

If a transaction references a customer/device that no longer exists:

The system should not crash.

Use:

```text
Unknown customer
Unknown device
```

and apply the defined risk policy.

---

# 92. Edge Case: Model Version Missing

Every risk assessment should have a model version.

If the model version is unavailable:

```text
Do not save an apparently valid AI assessment.
```

Record the evaluation failure.

---

# 93. Edge Case: Corrupted Model

If loading:

```text
risk_model.pkl
```

fails:

```text
Application startup health check
       ↓
Model unavailable
       ↓
Mark risk engine unhealthy
```

Do not wait until the first transaction to discover that the model is broken.

---

# 94. Health Checks

Provide endpoints such as:

```text
GET /health
GET /health/ready
```

### `/health`

Checks whether the application process is alive.

### `/health/ready`

Checks critical dependencies such as:

- Database
- Model availability
- Required configuration

Do not expose sensitive dependency details publicly.

---

# 95. Security Monitoring

Track unusual events:

```text
Repeated failed logins
Large number of API requests
Cross-merchant access attempts
Repeated 403 responses
Unexpected rule changes
Large numbers of transaction overrides
Unusual analyst behavior
```

These can later feed into a security dashboard.

---

# 96. Launch Security Checklist

Before launch:

- [ ] HTTPS enabled
- [ ] Debug mode disabled
- [ ] Strong JWT secret configured
- [ ] Secrets removed from Git
- [ ] Password hashing implemented
- [ ] Login rate limiting enabled
- [ ] Role-based authorization tested
- [ ] Merchant isolation tested
- [ ] PostgreSQL permissions restricted
- [ ] RLS policies tested
- [ ] Audit logs enabled
- [ ] Audit logs protected from modification
- [ ] SQL injection tests completed
- [ ] XSS tests completed
- [ ] CORS restricted
- [ ] Error messages sanitized
- [ ] Sensitive data excluded from logs
- [ ] Database backups configured
- [ ] Backup restoration tested
- [ ] Dependency vulnerabilities reviewed
- [ ] Model file protected
- [ ] Model failure behavior tested
- [ ] Database failure behavior tested
- [ ] Duplicate transaction handling tested
- [ ] Concurrent analyst actions tested

---

# 97. Security Testing Scenarios

At minimum, test these scenarios.

### Test 1 — Wrong Password

Expected:

```text
401
No account enumeration
```

### Test 2 — Expired JWT

Expected:

```text
401
```

### Test 3 — Analyst Creates Rule

Expected:

```text
403
```

### Test 4 — Merchant A Requests Merchant B Transaction

Expected:

```text
404 or access-safe denial
```

### Test 5 — SQL Injection Payload

Expected:

```text
Rejected / safely handled
```

### Test 6 — XSS Payload

Expected:

```text
Escaped / safely rendered
```

### Test 7 — Duplicate Transaction

Expected:

```text
No unintended duplicate
```

### Test 8 — Model Failure

Expected:

```text
No fake prediction
Controlled fallback
```

### Test 9 — Database Failure

Expected:

```text
503
No credentials leaked
```

### Test 10 — Analyst Override

Expected:

```text
Audit event created
```

---

# 98. Incident Response — MVP

If credentials are compromised:

```text
1. Disable affected account.
2. Rotate JWT/signing secrets if necessary.
3. Review audit logs.
4. Identify affected data.
5. Revoke active sessions/tokens where possible.
6. Patch the vulnerability.
7. Re-test security controls.
```

If the ML model is compromised:

```text
1. Disable affected model version.
2. Roll back to trusted model.
3. Preserve affected assessment records.
4. Investigate deployment history.
5. Re-evaluate impacted transactions if necessary.
```

---

# 99. Security Architecture

```text
                         ┌──────────────────────┐
                         │       Browser        │
                         │      React App       │
                         └──────────┬───────────┘
                                    │
                              HTTPS / TLS
                                    │
                                    ▼
                         ┌──────────────────────┐
                         │       FastAPI        │
                         │ Authentication       │
                         │ Authorization        │
                         │ Input Validation     │
                         │ Rate Limiting        │
                         └──────────┬───────────┘
                                    │
                   ┌────────────────┼─────────────────┐
                   ▼                ▼                 ▼
            ┌─────────────┐  ┌─────────────┐  ┌──────────────┐
            │ Risk Engine │  │ Audit Layer │  │ App Services │
            └──────┬──────┘  └──────┬──────┘  └──────┬───────┘
                   │                │                 │
                   └────────────────┼─────────────────┘
                                    ▼
                         ┌──────────────────────┐
                         │     PostgreSQL       │
                         │ Row-Level Security   │
                         │ Merchant Isolation   │
                         └──────────────────────┘
```

---

# 100. Recommended Security Architecture

The final MVP security stack should be:

```text
Authentication
    ↓
JWT / Secure Session

Authorization
    ↓
RBAC
    ↓
ADMIN / ANALYST

Data Isolation
    ↓
merchant_id
    ↓
PostgreSQL RLS

Input Security
    ↓
Pydantic Validation
    ↓
SQLAlchemy

Application Security
    ↓
Rate Limiting
    ↓
CORS
    ↓
HTTPS

AI Security
    ↓
Model Validation
    ↓
Model Versioning
    ↓
Controlled Deployment

Auditability
    ↓
Append-Only Audit Logs
```

---

# 101. What We Are NOT Doing in V1

To keep the project realistic, do not implement all enterprise security infrastructure immediately.

Not required for the MVP:

```text
Kubernetes security
Zero-trust enterprise network
Hardware security modules
Complex SIEM platform
Advanced behavioral biometrics
Multi-region disaster recovery
Enterprise SSO/SAML
SCIM provisioning
Advanced secrets orchestration
Dedicated fraud graph infrastructure
```

These are future-stage capabilities.

---

# 102. Security Priority Levels

## P0 — Must Fix Before Launch

- Authentication
- Authorization
- Merchant data isolation
- Password hashing
- JWT/session security
- Input validation
- SQL injection prevention
- XSS prevention
- Secure error handling
- Audit logging
- Secret protection
- HTTPS
- Model failure handling
- Database failure handling

## P1 — Strongly Recommended

- Rate limiting
- PostgreSQL RLS
- Security monitoring
- Backup/restore testing
- Dependency scanning
- Security headers
- Concurrent update protection

## P2 — Future

- Enterprise SSO
- MFA
- Advanced SIEM
- Device-based authentication
- Behavioral security analytics
- Dedicated security operations tooling

---

# 103. Final Security Principle

The most important rule for AI Risk Manager is:

> **Never allow convenience to override trust boundaries.**

A user should never see another merchant's data.

An Analyst should never silently change an Admin-controlled configuration.

An AI model should never be treated as infallible.

A failure should never quietly become an approval.

An audit record should never disappear because it is inconvenient.

The security architecture should therefore follow:

```text
Authenticate
      ↓
Authorize
      ↓
Validate
      ↓
Isolate
      ↓
Execute
      ↓
Audit
      ↓
Monitor
```

For an early-stage fintech risk product, this gives AI Risk Manager a strong security foundation without drowning the MVP in enterprise complexity.
