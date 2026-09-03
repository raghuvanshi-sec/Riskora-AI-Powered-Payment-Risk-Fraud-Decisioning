# AI Risk Manager — Frontend Specification Document

**Product:** AI Risk Manager — Razorpay Track  
**Document Type:** Frontend Specification & API Integration Specification  
**Version:** MVP / V1.0  
**Frontend:** React + JavaScript (ES6+)  
**Styling:** Vanilla CSS / CSS Modules  
**Backend:** FastAPI  
**Database:** PostgreSQL  
**Primary Users:** Admins and Risk Analysts

---

# 1. Document Purpose

This document defines the complete frontend experience for **AI Risk Manager**.

It establishes:

- Visual identity
- Design system
- Color palette
- Typography
- Spacing
- Layout rules
- Responsive behavior
- Components
- Page structure
- Navigation
- States and interactions
- Accessibility
- Frontend architecture
- API integration
- Authentication handling
- Error handling
- Third-party integration boundaries

The objective is to make the application feel like a **professional fintech risk-operations platform**, not a generic AI dashboard.

---

# 2. Product Experience

AI Risk Manager helps payment/risk teams:

1. Monitor transactions.
2. Detect suspicious activity.
3. Understand why a transaction was considered risky.
4. Investigate risk signals.
5. Approve, review, or block transactions.
6. Configure risk rules.
7. Track fraud/risk trends.

The frontend should therefore optimize for:

- Fast scanning
- Clear hierarchy
- High information density without clutter
- Strong visual distinction between risk states
- Explainable AI
- Reliable actions
- Operational confidence

---

# 3. UX Principles

## 3.1 Trust First

Every AI decision should be understandable.

Instead of:

> Risk Score: 87

show:

> **High Risk — 87/100**

with supporting signals such as:

```text
+ Unusual device
+ 7 failed attempts
+ High transaction velocity
+ New IP location
```

---

## 3.2 Action-Oriented Design

The dashboard should answer three questions quickly:

```text
What is happening?
Why is it happening?
What should I do?
```

---

## 3.3 Progressive Disclosure

Do not show every technical detail immediately.

Example:

```text
Transaction
   ↓
Risk Score
   ↓
Top Risk Factors
   ↓
Detailed Explanation
   ↓
Technical Model Details
```

---

## 3.4 Consistency

The same risk state must always use the same:

- Label
- Icon
- Visual treatment
- Meaning
- Action behavior

---

# 4. Brand Direction

## Visual Personality

AI Risk Manager should feel:

- Secure
- Intelligent
- Precise
- Modern
- Professional
- Calm under pressure
- Fintech-native

Avoid:

- Excessive gradients
- Neon cyberpunk styling
- Overly playful illustrations
- Excessive glassmorphism
- Decorative animations that distract from operational information

---

# 5. Color System

The interface uses a restrained dark fintech palette with clear semantic colors.

## 5.1 Core Colors

| Token | Hex | Usage |
|---|---|---|
| `--color-bg` | `#0B1020` | Main application background |
| `--color-surface` | `#111827` | Cards and panels |
| `--color-surface-raised` | `#172033` | Elevated components |
| `--color-border` | `#273449` | Borders/dividers |
| `--color-text-primary` | `#F8FAFC` | Primary text |
| `--color-text-secondary` | `#A7B0C0` | Secondary text |
| `--color-text-muted` | `#6B768A` | Supporting text |
| `--color-primary` | `#635BFF` | Primary actions |
| `--color-primary-hover` | `#5148E5` | Primary hover |
| `--color-focus` | `#8B85FF` | Keyboard focus |

---

# 6. Semantic Risk Colors

Risk states must be immediately recognizable.

| State | Hex | Meaning |
|---|---|---|
| Low Risk | `#22C55E` | Safe / low concern |
| Medium Risk | `#F59E0B` | Requires attention |
| High Risk | `#EF4444` | Strong fraud indicators |
| Critical | `#DC2626` | Immediate intervention |
| Informational | `#3B82F6` | Neutral information |

Do not use semantic colors as decoration.

They should communicate meaning.

---

# 7. Status Backgrounds

Use subtle backgrounds rather than filling entire cards with bright colors.

Example:

```css
.risk-high {
  color: #EF4444;
  background: rgba(239, 68, 68, 0.10);
}
```

Recommended pattern:

```text
Icon + Label + Subtle Background
```

rather than:

```text
Entire card = Red
```

---

# 8. Typography

## Primary Font

Recommended:

**Inter**

Reason:

- Excellent readability
- Strong UI typography
- Clear numerical glyphs
- Good dashboard readability
- Widely supported

Fallback:

```css
font-family:
  Inter,
  system-ui,
  -apple-system,
  BlinkMacSystemFont,
  "Segoe UI",
  sans-serif;
```

---

# 9. Typography Scale

| Token | Size | Weight | Usage |
|---|---:|---:|---|
| Display | 32px | 700 | Major dashboard KPI |
| H1 | 28px | 700 | Page title |
| H2 | 22px | 650 | Section title |
| H3 | 18px | 600 | Card title |
| Body Large | 16px | 400 | Important body text |
| Body | 14px | 400 | Standard UI |
| Small | 13px | 400 | Metadata |
| Caption | 12px | 500 | Labels |
| Micro | 11px | 500 | Dense metadata |

---

# 10. Numerical Typography

Risk scores, transaction amounts, counts, and percentages should use:

```css
font-variant-numeric: tabular-nums;
```

This keeps numbers aligned in dashboards.

Example:

```text
₹ 1,25,000.00
87
12.4%
1,248
```

---

# 11. Spacing System

Use a 4px base grid.

```text
4px
8px
12px
16px
20px
24px
32px
40px
48px
64px
80px
```

Recommended CSS variables:

```css
--space-1: 4px;
--space-2: 8px;
--space-3: 12px;
--space-4: 16px;
--space-5: 20px;
--space-6: 24px;
--space-8: 32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

---

# 12. Border Radius

Use moderate rounding.

```text
Small: 6px
Default: 8px
Large: 12px
Modal: 16px
Pill: 999px
```

Avoid excessive rounded-card styling.

---

# 13. Shadows

The dark interface should rely more on borders than dramatic shadows.

Recommended:

```css
box-shadow:
  0 8px 24px rgba(0, 0, 0, 0.20);
```

Use shadows primarily for:

- Modals
- Dropdowns
- Floating panels
- Elevated menus

---

# 14. Grid System

Desktop:

```text
12-column grid
```

Recommended:

```text
Page padding: 32px
Column gap: 20–24px
```

Tablet:

```text
8-column grid
```

Mobile:

```text
4-column grid
```

---

# 15. Main Application Layout

```text
┌─────────────────────────────────────────────────────┐
│ Top Bar                                             │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│ Sidebar      │ Main Content                         │
│              │                                      │
│ Dashboard    │                                      │
│ Transactions │                                      │
│ Alerts       │                                      │
│ Analytics    │                                      │
│ Rules        │                                      │
│              │                                      │
│ Settings     │                                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

---

# 16. Sidebar

Width:

```text
240px
```

Collapsed:

```text
72px
```

Sidebar sections:

```text
AI RISK MANAGER

Overview
Transactions
Risk Queue
Alerts
Analytics

CONFIGURATION

Risk Rules
Settings
```

Bottom:

```text
User Avatar
User Name
Role
Logout
```

---

# 17. Top Bar

Contains:

- Page title/breadcrumb
- Search
- Notifications
- User menu

Example:

```text
Transactions              Search      🔔     Satyam ▼
```

---

# 18. Dashboard Page

Primary dashboard sections:

```text
┌────────────────────────────────────────────┐
│ Risk Overview                               │
├────────┬────────┬────────┬─────────────────┤
│ Volume │ Fraud  │ Review │ Blocked         │
└────────┴────────┴────────┴─────────────────┘

┌─────────────────────┬──────────────────────┐
│ Risk Trend          │ Risk Distribution    │
│                     │                      │
└─────────────────────┴──────────────────────┘

┌────────────────────────────────────────────┐
│ High-Risk Transactions                     │
└────────────────────────────────────────────┘
```

---

# 19. KPI Cards

Each KPI card contains:

```text
Label
Value
Change
Time period
Optional icon
```

Example:

```text
HIGH-RISK TRANSACTIONS

142

↑ 12.4%
vs last 24h
```

Cards should not become clickable unless they actually lead somewhere.

---

# 20. Transaction Table

Columns:

| Column | Purpose |
|---|---|
| Transaction ID | Identification |
| Customer | Customer identity |
| Amount | Transaction value |
| Risk Score | AI risk score |
| Risk Level | Low/Medium/High |
| Status | Current decision |
| Time | Transaction timestamp |
| Action | Open details |

---

# 21. Table Behavior

Required:

- Sorting
- Pagination
- Filtering
- Search
- Loading state
- Empty state
- Error state

Optional for V1:

- Column customization
- CSV export

---

# 22. Risk Score Component

Example:

```text
87 / 100
HIGH RISK
```

Use:

- Numeric score
- Risk label
- Progress/ring indicator
- Top factors

Avoid relying only on color.

A screen-reader-accessible label should communicate:

```text
Risk score 87 out of 100, high risk.
```

---

# 23. Transaction Details Page

Structure:

```text
← Transactions

Transaction #TXN-92837

₹24,500
HIGH RISK

[BLOCK] [APPROVE] [REVIEW]

────────────────────────────

Risk Assessment

87 / 100

Top Risk Factors
• New device
• High velocity
• IP mismatch

────────────────────────────

Transaction Information

Amount
Currency
Payment Method
Timestamp

────────────────────────────

Customer Information

Customer ID
Account age
Previous transactions

────────────────────────────

Decision History
```

---

# 24. AI Explanation Panel

This is one of the product's differentiating components.

Example:

```text
Why was this transaction flagged?

HIGH RISK

1. Unusual transaction velocity
   8 attempts in 3 minutes

2. New device
   Device has not been seen before

3. Location anomaly
   Current IP differs significantly
   from historical activity

Recommendation:
Manual review recommended.
```

The explanation should use plain English.

---

# 25. Risk Factors

Each factor should contain:

```text
Icon
Factor name
Severity
Explanation
Evidence
```

Example:

```text
⚠ High

Transaction Velocity

8 transactions in 3 minutes.

Typical customer behavior:
1–2 transactions per session.
```

---

# 26. Decision Buttons

Primary actions:

```text
APPROVE
REVIEW
BLOCK
```

Recommended styling:

- Approve → positive semantic styling
- Review → warning styling
- Block → destructive styling

Destructive actions should require confirmation when appropriate.

---

# 27. Button Design

## Primary Button

```text
Height: 40px
Padding: 0 16px
Radius: 8px
Weight: 600
```

Example:

```text
[ Run Risk Analysis ]
```

---

## Secondary Button

Transparent or surface background.

Example:

```text
[ View Details ]
```

---

## Destructive Button

Used for:

```text
Block
Delete
Disable
```

Should clearly communicate consequence.

---

# 28. Button States

Every button must support:

```text
Default
Hover
Active
Focus
Disabled
Loading
Success
```

Loading:

```text
[ ◌ Processing... ]
```

Never allow multiple submissions while an action is processing.

---

# 29. Input Fields

Input structure:

```text
Label
Input
Helper text
Error
```

Example:

```text
Transaction ID

[ TXN-92837                     ]

Search by transaction ID
```

---

# 30. Input States

Support:

```text
Default
Hover
Focus
Filled
Disabled
Error
Success
```

Focus state must be visible.

---

# 31. Search

Global search should support:

```text
Transaction ID
Customer ID
Email
Risk status
```

Example:

```text
Search transactions...
```

Do not search across unauthorized merchant data.

---

# 32. Select / Dropdown

Use dropdowns for:

```text
Risk level
Status
Payment method
Time period
```

For large lists, use searchable selects.

---

# 33. Filters

Transaction filters:

```text
Risk Level
Status
Amount
Date
Payment Method
```

Example:

```text
[ Risk: High ▼ ]
[ Status: Review ▼ ]
[ Last 24h ▼ ]
```

---

# 34. Modal Design

Modal:

```text
Width:
Small → 400px
Medium → 520px
Large → 720px
```

Structure:

```text
Title
Description
Content

Cancel          Confirm
```

---

# 35. Block Confirmation Modal

Example:

```text
Block transaction?

Transaction #TXN-92837
₹24,500

This transaction will be marked as blocked.

Reason

[________________________________]

[ Cancel ]     [ Block Transaction ]
```

Require a reason for manual overrides.

---

# 36. Toast Notifications

Use toasts for:

- Successful updates
- Non-blocking failures
- Background events

Examples:

```text
✓ Transaction blocked successfully.
```

```text
Risk rule updated successfully.
```

Do not use toasts for critical information that must remain visible.

---

# 37. Alerts

Alerts are persistent contextual messages.

Example:

```text
⚠ Risk engine unavailable

AI assessment is temporarily unavailable.
Transactions may require manual review.
```

---

# 38. Empty States

Example:

```text
No high-risk transactions

There are currently no transactions
requiring immediate attention.
```

Avoid empty screens with no explanation.

---

# 39. Loading States

Use skeletons instead of spinners for content-heavy screens.

Example:

```text
████████████
████████
████████████████
```

For actions:

```text
Processing...
```

---

# 40. Error States

Example:

```text
Unable to load transactions

Something went wrong while retrieving
your transaction data.

[ Try Again ]
```

Do not expose stack traces.

---

# 41. 404 Page

Example:

```text
Transaction not found

The transaction may have been removed,
or you may not have access to it.

[ Back to Transactions ]
```

This deliberately avoids revealing cross-merchant data.

---

# 42. 403 Page

Example:

```text
Access restricted

You don't have permission to perform
this action.
```

---

# 43. 500 Page

Example:

```text
Something went wrong

We couldn't complete your request.

Request ID:
req_abc123

[ Try Again ]
```

---

# 44. Responsive Design

## Desktop

Primary target:

```text
1440px
```

Supported:

```text
1280px+
```

Use full sidebar and multi-column dashboard.

---

## Tablet

```text
768px–1279px
```

Collapse sidebar where necessary.

Reduce:

- Table columns
- Card spacing
- Dashboard density

---

## Mobile

```text
<768px
```

Use:

- Bottom navigation or collapsible menu
- Horizontally scrollable tables
- Stacked KPI cards
- Full-width actions
- Full-screen modals

The core transaction investigation workflow must remain usable on mobile.

---

# 45. Accessibility

Target:

**WCAG 2.2 AA**

Requirements:

- Keyboard navigation
- Visible focus states
- Semantic HTML
- ARIA labels where necessary
- Sufficient color contrast
- No color-only communication
- Accessible modal focus management
- Accessible form errors
- Screen-reader-friendly risk labels

---

# 46. Motion

Animations should be subtle.

Use:

```text
150–250ms
```

for:

- Hover
- Dropdowns
- Modal entry
- Sidebar transitions

Avoid animation on every dashboard element.

Risk operations should feel stable and deliberate.

---

# 47. Iconography

Use one consistent icon library.

Recommended:

**Lucide React**

Use icons for:

- Navigation
- Actions
- Risk signals
- Status
- Alerts

Never rely on an icon alone for a critical action.

---

# 48. Frontend Architecture

Recommended:

```text
src/
├── app/
│   ├── App.jsx
│   ├── router.jsx
│   └── providers/
│
├── assets/
│
├── components/
│   ├── common/
│   ├── layout/
│   ├── dashboard/
│   ├── transactions/
│   ├── risk/
│   ├── alerts/
│   └── rules/
│
├── pages/
│   ├── Login/
│   ├── Dashboard/
│   ├── Transactions/
│   ├── TransactionDetails/
│   ├── Alerts/
│   ├── Analytics/
│   ├── RiskRules/
│   └── Settings/
│
├── services/
│   ├── api.js
│   ├── authApi.js
│   ├── transactionApi.js
│   ├── riskApi.js
│   ├── alertApi.js
│   └── ruleApi.js
│
├── hooks/
│
├── context/
│
├── utils/
│
├── styles/
│   ├── tokens.css
│   ├── globals.css
│   └── components.css
│
└── main.jsx
```

---

# 49. API Client

Create a centralized API client.

Example:

```text
src/services/api.js
```

Responsibilities:

- Base URL
- Authentication
- Headers
- JSON parsing
- Error normalization
- Request ID handling
- Timeout handling

Do not duplicate fetch configuration throughout components.

---

# 50. Environment Variables

Frontend:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

Production example:

```env
VITE_API_BASE_URL=https://api.example.com/api/v1
```

Important:

> Anything prefixed with `VITE_` is available to the frontend build and should be considered public.

Never put secrets in frontend environment variables.

---

# 51. Authentication API

## Login

```http
POST /api/v1/auth/login
```

Request:

```json
{
  "email": "analyst@example.com",
  "password": "********"
}
```

Expected response:

```json
{
  "success": true,
  "data": {
    "user": {
      "id": "uuid",
      "name": "Risk Analyst",
      "email": "analyst@example.com",
      "role": "ANALYST",
      "merchant_id": "uuid"
    },
    "access_token": "..."
  }
}
```

The production session design should use secure token/cookie handling consistent with the backend security document.

---

# 52. Current User

```http
GET /api/v1/auth/me
```

Response:

```json
{
  "id": "uuid",
  "name": "Risk Analyst",
  "email": "analyst@example.com",
  "role": "ANALYST",
  "merchant_id": "uuid"
}
```

Used during application initialization.

---

# 53. Logout

```http
POST /api/v1/auth/logout
```

Response:

```json
{
  "success": true,
  "message": "Logged out successfully"
}
```

The frontend clears its authentication state.

If server-side sessions/refresh tokens are used, the backend must revoke them as appropriate.

---

# 54. Dashboard API

```http
GET /api/v1/dashboard/summary
```

Expected response:

```json
{
  "transaction_volume": 12480,
  "high_risk_count": 142,
  "review_count": 83,
  "blocked_count": 37,
  "fraud_rate": 1.84,
  "period": "24h"
}
```

---

# 55. Risk Distribution API

```http
GET /api/v1/dashboard/risk-distribution
```

Response:

```json
{
  "low": 8200,
  "medium": 3800,
  "high": 480
}
```

---

# 56. Risk Trend API

```http
GET /api/v1/dashboard/risk-trend?period=7d
```

Response:

```json
{
  "period": "7d",
  "data": [
    {
      "date": "2026-08-23",
      "low": 1200,
      "medium": 540,
      "high": 72
    }
  ]
}
```

---

# 57. Transactions API

## List Transactions

```http
GET /api/v1/transactions
```

Query parameters:

```text
page
limit
search
risk_level
status
date_from
date_to
sort
```

Example:

```http
GET /api/v1/transactions?page=1&limit=25&risk_level=HIGH
```

Response:

```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "transaction_id": "TXN-92837",
      "amount": 24500,
      "currency": "INR",
      "risk_score": 87,
      "risk_level": "HIGH",
      "status": "REVIEW",
      "created_at": "2026-08-29T12:30:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 25,
    "total": 142
  }
}
```

---

# 58. Transaction Details API

```http
GET /api/v1/transactions/{transaction_id}
```

Response:

```json
{
  "id": "uuid",
  "transaction_id": "TXN-92837",
  "amount": 24500,
  "currency": "INR",
  "payment_method": "CARD",
  "customer": {
    "id": "uuid",
    "account_age_days": 12
  },
  "risk": {
    "score": 87,
    "level": "HIGH",
    "recommended_action": "BLOCK",
    "model_version": "v1.2.0",
    "factors": [
      {
        "name": "Transaction Velocity",
        "severity": "HIGH",
        "description": "8 attempts in 3 minutes"
      }
    ]
  }
}
```

---

# 59. Run Risk Analysis API

```http
POST /api/v1/risk/evaluate
```

Request:

```json
{
  "transaction_id": "TXN-92837"
}
```

Response:

```json
{
  "risk_score": 87,
  "risk_level": "HIGH",
  "recommended_action": "REVIEW",
  "model_version": "v1.2.0",
  "factors": [
    {
      "name": "High Velocity",
      "severity": "HIGH",
      "description": "8 transactions detected within 3 minutes."
    }
  ]
}
```

The frontend should never calculate the authoritative risk score.

---

# 60. Transaction Decision API

## Approve

```http
POST /api/v1/transactions/{id}/approve
```

Request:

```json
{
  "reason": "Verified customer activity"
}
```

Response:

```json
{
  "success": true,
  "status": "APPROVED"
}
```

---

## Block

```http
POST /api/v1/transactions/{id}/block
```

Request:

```json
{
  "reason": "Multiple suspicious signals detected"
}
```

Response:

```json
{
  "success": true,
  "status": "BLOCKED"
}
```

---

## Review

```http
POST /api/v1/transactions/{id}/review
```

Request:

```json
{
  "reason": "Requires manual verification"
}
```

---

# 61. Risk Rules API

## List Rules

```http
GET /api/v1/risk-rules
```

Response:

```json
[
  {
    "id": "uuid",
    "name": "High Transaction Velocity",
    "field": "transaction_count",
    "operator": ">",
    "value": 5,
    "action": "REVIEW",
    "enabled": true
  }
]
```

---

# 62. Create Rule

Admin only:

```http
POST /api/v1/risk-rules
```

Request:

```json
{
  "name": "High Transaction Velocity",
  "field": "transaction_count",
  "operator": ">",
  "value": 5,
  "action": "REVIEW"
}
```

Response:

```json
{
  "id": "uuid",
  "name": "High Transaction Velocity",
  "enabled": true
}
```

---

# 63. Update Rule

```http
PATCH /api/v1/risk-rules/{id}
```

Example:

```json
{
  "enabled": false
}
```

Only authorized Admin users may perform configuration changes.

---

# 64. Alerts API

## List Alerts

```http
GET /api/v1/alerts
```

Query:

```text
page
limit
severity
status
```

Response:

```json
{
  "data": [
    {
      "id": "uuid",
      "type": "HIGH_RISK_TRANSACTION",
      "severity": "HIGH",
      "message": "High-risk transaction detected.",
      "transaction_id": "TXN-92837",
      "read": false,
      "created_at": "2026-08-29T12:30:00Z"
    }
  ]
}
```

---

# 65. Mark Alert Read

```http
PATCH /api/v1/alerts/{id}
```

Request:

```json
{
  "read": true
}
```

---

# 66. Analytics API

```http
GET /api/v1/analytics/overview?period=30d
```

Response:

```json
{
  "transactions": 184200,
  "high_risk": 4820,
  "blocked": 1420,
  "reviewed": 2680,
  "estimated_fraud_prevented": 820000,
  "false_positive_rate": 4.2
}
```

Analytics should be treated as backend-derived data, not calculations performed independently by the frontend.

---

# 67. API Error Contract

All APIs should use a consistent error structure.

```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request.",
    "request_id": "req_abc123",
    "details": []
  }
}
```

Frontend maps known error codes to appropriate UI behavior.

---

# 68. Frontend Error Mapping

| HTTP | Frontend Behavior |
|---|---|
| 400 | Show validation error |
| 401 | Re-authenticate |
| 403 | Show permission error |
| 404 | Show not-found/access-safe state |
| 409 | Show conflict and refresh |
| 422 | Show field validation |
| 429 | Show rate-limit message |
| 500 | Generic server error |
| 503 | Service unavailable |
| Network error | Retry / offline message |

---

# 69. API Request Lifecycle

Every request should follow:

```text
Component
   ↓
Service Function
   ↓
API Client
   ↓
Authentication
   ↓
HTTP Request
   ↓
Backend
   ↓
Response
   ↓
Normalize
   ↓
Component State
```

Avoid making raw API calls directly from every UI component.

---

# 70. Third-Party Services

The MVP should minimize third-party dependencies.

Recommended integrations:

| Service | Purpose | Required V1? |
|---|---|---|
| PostgreSQL | Application database | Yes |
| FastAPI | Backend API | Yes |
| Risk ML model | Risk scoring | Yes |
| Lucide React | Icons | Yes |
| Inter font | Typography | Recommended |
| Chart library | Dashboard visualization | Recommended |
| Email provider | Password reset/notifications | Optional |
| Sentry | Error monitoring | Recommended for deployment |
| Razorpay APIs | Payment data integration | Depends on track scope |

---

# 71. PostgreSQL Integration

PostgreSQL is not called directly by the frontend.

Architecture:

```text
React
 ↓
FastAPI
 ↓
SQLAlchemy
 ↓
PostgreSQL
```

Frontend only consumes API responses.

No database credentials belong in the frontend.

---

# 72. ML Model Integration

The frontend does not communicate directly with the ML model.

Correct:

```text
React
 ↓
FastAPI
 ↓
Risk Engine
 ↓
ML Model
```

The API returns:

```text
score
risk level
recommended action
model version
risk factors
```

---

# 73. Razorpay Integration

If the Razorpay track requires actual Razorpay transaction/payment data, integrate through the backend.

Architecture:

```text
Razorpay
    ↓
Backend Integration
    ↓
Risk Engine
    ↓
PostgreSQL
    ↓
React Dashboard
```

Never expose Razorpay secret credentials in React.

If the project is only a demonstration/prototype and no live Razorpay API access is required, use controlled mock transaction data instead of inventing credentials or undocumented endpoints.

---

# 74. Razorpay API Boundary

The exact Razorpay endpoints should be selected from the currently enabled Razorpay product/API documentation and the credentials available to the project.

Frontend requirement:

```text
NO direct Razorpay secret API calls from browser
```

Frontend only calls:

```text
GET /api/v1/transactions
```

or other internal FastAPI endpoints.

---

# 75. Webhook Architecture

If payment events are received from Razorpay or another payment provider:

```text
Payment Provider
       ↓
Webhook Endpoint
       ↓
Signature Verification
       ↓
Validate Event
       ↓
Store Event
       ↓
Risk Engine
       ↓
Update Transaction
       ↓
Frontend Refresh
```

The frontend should never be responsible for verifying payment-provider webhook signatures.

---

# 76. Webhook Idempotency

Webhook events may be delivered more than once.

Use:

```text
provider_event_id
```

with a unique constraint.

Expected behavior:

```text
First event
→ Process

Duplicate event
→ Ignore/reuse existing result
```

---

# 77. Email Integration

If password reset or alert emails are implemented, use a transactional email provider.

Example abstraction:

```text
FastAPI
   ↓
Email Service
   ↓
Provider
```

The frontend calls:

```http
POST /api/v1/auth/forgot-password
```

It should not call the email provider directly.

---

# 78. Error Monitoring — Sentry

If Sentry is selected for production monitoring:

```text
React
 ↓
Sentry SDK
 ↓
Error Monitoring
```

Do not send:

- Passwords
- Tokens
- Card data
- CVV
- Full sensitive transaction payloads

Configure scrubbing before production.

---

# 79. Chart Library

A charting library can be used for:

- Risk trend
- Transaction volume
- Risk distribution
- Fraud rate
- Approval/block/review trends

The chart library consumes backend data.

It should not become the source of truth for metrics.

---

# 80. Data Fetching Strategy

For MVP, use a simple server-state pattern.

Recommended options:

- TanStack Query
- Custom hooks with fetch

If using TanStack Query:

```text
useTransactions()
useTransaction()
useDashboard()
useRiskRules()
useAlerts()
```

Benefits:

- Caching
- Loading states
- Retry
- Refetching
- Mutation handling

---

# 81. State Management

Do not put everything into global state.

Use:

### Local State

For:

- Modal visibility
- Form values
- Filters

### Server State

For:

- Transactions
- Alerts
- Dashboard data
- Risk assessments

### Global State

Only for:

- Authentication/session
- Theme
- Merchant context if required

---

# 82. Caching

Good candidates:

```text
Dashboard summary
Risk rules
Analytics
```

Short-lived caching is appropriate.

Do not cache sensitive transaction data indefinitely in the browser.

---

# 83. Optimistic Updates

Use carefully.

Safe examples:

```text
Mark alert as read
```

Risky examples:

```text
Block transaction
Approve transaction
```

For financial-risk decisions, wait for backend confirmation before presenting the action as final.

---

# 84. Polling

For an MVP, polling can provide near-real-time updates.

Example:

```text
Risk queue refresh
every 15–30 seconds
```

Do not poll excessively.

Future version:

```text
WebSocket / Server-Sent Events
```

---

# 85. Authentication Route Protection

Routes:

```text
/login
```

Public.

All other application routes:

```text
/dashboard
/transactions
/transactions/:id
/alerts
/analytics
/risk-rules
/settings
```

require authentication.

---

# 86. Role-Based Route Protection

Example:

```text
/risk-rules
```

may be accessible to:

```text
ADMIN
```

only for modification.

Analysts may have read access if product requirements allow it.

Frontend restrictions are not sufficient.

Backend authorization must always enforce permissions.

---

# 87. URL Design

Recommended:

```text
/dashboard

/transactions
/transactions/:id

/risk-queue

/alerts

/analytics

/risk-rules

/settings
```

Use human-readable URLs where practical.

---

# 88. Form Validation

Validate on:

```text
Input
Blur
Submit
```

Do not rely only on frontend validation.

Backend validation remains authoritative.

---

# 89. Transaction Search UX

Search should support:

```text
TXN-92837
Customer ID
Email
```

Debounce free-text searches.

Recommended:

```text
250–400ms
```

Do not send an API request on every keystroke.

---

# 90. Pagination

Use server-side pagination.

Example:

```text
Page 1 of 58

< Previous
1 2 3 ... 58
Next >
```

Do not load thousands of transactions into the browser at once.

---

# 91. Security UX

Security should be visible but not intrusive.

Examples:

```text
Last login
Current role
Session status
Audit history
```

Sensitive operations should request confirmation.

---

# 92. Audit UI

Admin can see:

```text
Timestamp
User
Action
Resource
Result
IP/device metadata if approved by product/security policy
```

Example:

```text
12:31 PM
Admin
Updated risk rule
High Velocity Rule
Success
```

Audit records should be read-only in the UI.

---

# 93. Risk Rules UI

Admin screen:

```text
Risk Rules

[ + Create Rule ]

Rule Name          Condition        Action      Status
High Velocity      > 5 / 3 min      REVIEW      ON
New Device         = true            REVIEW      ON
IP Mismatch        = true            REVIEW      OFF
```

Use a confirmation step before disabling important rules.

---

# 94. Rule Builder

Use controlled fields:

```text
Field
Operator
Value
Action
```

Example:

```text
Transaction Count
       >
5
       →
REVIEW
```

Do not expose arbitrary code execution.

---

# 95. AI Confidence

If the model provides confidence, show it only if it has a clearly defined meaning.

Do not confuse:

```text
Risk Score
```

with:

```text
Model Confidence
```

These are different concepts.

---

# 96. Explainability UX Rule

Never write:

> The AI knows this transaction is fraudulent.

Prefer:

> The risk model assigned a high-risk score based on these signals.

This maintains appropriate user trust.

---

# 97. Notifications

Notification categories:

```text
High-risk transaction
Risk engine failure
Rule change
System alert
```

Avoid excessive notifications.

---

# 98. Offline / Network Failure

If the network disconnects:

```text
Connection lost

Some information may be outdated.

[ Retry ]
```

Do not allow stale transaction information to be mistaken for a confirmed current decision.

---

# 99. Stale Data

If transaction information is older than a defined refresh window, show:

```text
Last updated 28 seconds ago
```

For critical actions, refresh the transaction before submission if concurrency or freshness matters.

---

# 100. Frontend Performance Targets

Target:

```text
Initial page load: < 3 seconds
Dashboard interaction: < 100ms perceived response
API-driven pages: skeleton within 100ms
```

Use:

- Code splitting
- Lazy-loaded pages
- Optimized assets
- Server pagination
- Query caching
- Minimal bundle size

---

# 101. Frontend Security Checklist

Before launch:

- [ ] No secrets in frontend
- [ ] HTTPS enabled
- [ ] Protected routes
- [ ] Backend authorization enforced
- [ ] CORS configured
- [ ] XSS-safe rendering
- [ ] No dangerous HTML injection
- [ ] API errors sanitized
- [ ] Sensitive data not stored unnecessarily
- [ ] Secure authentication/session implementation
- [ ] Rate limiting handled server-side
- [ ] Dependency vulnerabilities reviewed
- [ ] Production source maps reviewed
- [ ] Security headers configured
- [ ] Third-party scripts minimized
- [ ] Sentry data scrubbing configured if used

---

# 102. MVP Pages

The minimum frontend should contain:

## 1. Login

```text
Email
Password
Login
```

## 2. Dashboard

```text
KPIs
Risk distribution
Risk trend
High-risk queue
```

## 3. Transactions

```text
Search
Filters
Transaction table
Pagination
```

## 4. Transaction Details

```text
Transaction information
Risk score
Risk factors
AI explanation
Approve
Review
Block
Decision history
```

## 5. Alerts

```text
Alert list
Severity
Transaction link
Read/unread
```

## 6. Risk Rules

Admin-focused:

```text
View rules
Create
Edit
Enable/disable
```

## 7. Settings

```text
User profile
Merchant settings
```

---

# 103. Nice-to-Have Frontend Features

Not required for V1:

- Dark/light theme switching
- Advanced saved filters
- Custom dashboard builder
- CSV export
- Bulk transaction actions
- Real-time WebSockets
- Advanced graph visualization
- Keyboard command palette
- AI conversational assistant
- Custom report builder

---

# 104. Frontend Development Priority

## Phase 1 — Foundation

```text
React setup
Routing
Design tokens
Layout
Authentication
API client
```

## Phase 2 — Core Workflow

```text
Dashboard
Transactions
Transaction details
Risk score
Risk factors
Decision actions
```

## Phase 3 — Operations

```text
Alerts
Risk queue
Risk rules
Analytics
```

## Phase 4 — Hardening

```text
Error states
Loading states
Accessibility
Responsive design
Security review
Performance
```

---

# 105. Final Frontend Architecture

```text
                     ┌─────────────────────┐
                     │      React App      │
                     └──────────┬──────────┘
                                │
                 ┌──────────────┼──────────────┐
                 ▼              ▼              ▼
            UI Components   Pages/Routes   State/Queries
                 │              │              │
                 └──────────────┼──────────────┘
                                ▼
                         API Service Layer
                                │
                           HTTPS / JSON
                                │
                                ▼
                         ┌──────────────┐
                         │   FastAPI    │
                         └──────┬───────┘
                                │
             ┌──────────────────┼─────────────────┐
             ▼                  ▼                 ▼
        Risk Engine         PostgreSQL       Integrations
             │                                    │
             ▼                                    ▼
          ML Model                          Payment Provider
```

---

# 106. Design System Summary

The AI Risk Manager UI should feel:

```text
Dark
Precise
Professional
Data-dense
Trustworthy
Fast
Explainable
Operational
```

Core visual language:

```text
#0B1020  → Background
#111827  → Surface
#635BFF  → Primary
#22C55E  → Low Risk / Positive
#F59E0B  → Medium / Warning
#EF4444  → High / Destructive
#F8FAFC  → Primary Text
#A7B0C0  → Secondary Text
```

Typography:

```text
Inter
```

Spacing:

```text
4px base grid
```

Primary architecture:

```text
React
   ↓
Service Layer
   ↓
FastAPI
   ↓
PostgreSQL + Risk Engine
```

---

# 107. Definition of Done — Frontend MVP

The frontend is considered MVP-ready when:

- [ ] User can log in securely.
- [ ] Dashboard loads real backend data.
- [ ] Transactions can be searched and filtered.
- [ ] Transaction details show risk score and explanation.
- [ ] Risk factors are understandable.
- [ ] Analyst can approve/review/block according to permissions.
- [ ] Admin can manage risk rules.
- [ ] Alerts are visible.
- [ ] Loading states exist.
- [ ] Empty states exist.
- [ ] Error states exist.
- [ ] Unauthorized actions are blocked.
- [ ] Responsive layouts work.
- [ ] Keyboard navigation works for critical flows.
- [ ] API errors are normalized.
- [ ] No secrets are shipped to the browser.
- [ ] Third-party credentials remain server-side.
- [ ] Critical decisions are confirmed by the backend.
- [ ] Production security review is completed.

---

# 108. Final Product Principle

The frontend is not simply a dashboard.

It is the **control room for financial-risk decisions**.

Every component should therefore answer one of three needs:

```text
OBSERVE
What is happening?

UNDERSTAND
Why is it happening?

ACT
What should I do?
```

The interface should make those three steps almost effortless.

A strong AI Risk Manager frontend should not overwhelm the analyst with AI jargon or visual noise. It should turn complex transaction signals into a clear operational story:

```text
Transaction
     ↓
Risk Score
     ↓
Evidence
     ↓
Explanation
     ↓
Recommended Action
     ↓
Human Decision
     ↓
Auditable Outcome
```

That is the core UX loop of the product.
