# Client Review (2026-02-09)

Scope reviewed:
- `client/src/**` and `client/vite.config.js`
- Skipped `client/node_modules/**`, `client/package.json`, and `client/package-lock.json` per request.

## Critical Findings

1. Legacy API contract is still used across the app; backend has moved to REST resource routes.
- Impact: most data operations will 404/405 against current backend.
- Evidence (client):
  - `src/utils/api.jsx:2`
  - `src/utils/api.jsx:11`
  - `src/utils/api.jsx:20`
  - `src/utils/api.jsx:29`
  - `src/utils/api.jsx:38`
  - `src/routes/home/homepages/ticket/Ticket.jsx:102`
  - `src/routes/home/homepages/ticket/TicketTest.jsx:220`
  - `src/routes/home/homepages/search/Search.jsx:76`
  - `src/routes/home/homepages/search/Search.jsx:147`
  - `src/routes/home/homepages/search/Search.jsx:189`
  - `src/routes/home/homepages/search/Search.jsx:210`
  - `src/routes/home/homepages/search/Search.jsx:234`
  - `src/routes/home/homepages/search/SearchTest.jsx:81`
  - `src/routes/home/homepages/search/SearchTest.jsx:173`
  - `src/routes/home/homepages/search/SearchTest.jsx:194`
  - `src/routes/home/homepages/search/SearchTest.jsx:218`
  - `src/routes/settings/settingspages/locations/Locations.jsx:33`
  - `src/routes/settings/settingspages/locations/Locations.jsx:72`
  - `src/routes/settings/settingspages/locations/Locations.jsx:105`
  - `src/routes/settings/settingspages/locations/Locations.jsx:136`
  - `src/routes/settings/settingspages/users/Users.jsx:39`
  - `src/routes/settings/settingspages/users/Users.jsx:40`
  - `src/routes/auth/edit/EditUser.jsx:57`
  - `src/routes/home/homepages/deduction/Deduction.jsx:35`
  - `src/routes/home/homepages/deduction/Deduction.jsx:51`
  - `src/routes/home/homepages/deduction/Deduction.jsx:79`
  - `src/routes/reports/reportpages/ticket_list/TicketList.jsx:44`
- Evidence (backend canonical pattern):
  - `server/app/core/resource.py:24` (`GET /<resource>`)
  - `server/app/core/resource.py:31` (`POST /<resource>`)
  - `server/app/core/resource.py:39` (`PATCH /<resource>/<id>`)
  - `server/app/core/resource.py:47` (`DELETE /<resource>/<id>`)
  - `server/app/api/ticket.py:27` (`tickets`)
  - `server/app/api/transaction.py:24` (`transactions`)
  - `server/app/api/user.py:24` (`users`)
  - `server/app/api/location.py:24` (`locations`)
  - `server/app/api/sales_category.py:24` (`sales_categories`)
  - `server/app/api/payment_type.py:24` (`payment_types`)

2. Logout request uses wrong HTTP method.
- Impact: logout will fail (backend defines POST-only endpoint).
- Evidence (client): `src/layout/RootLayout.jsx:14` uses `fetch("/api/auth/logout")` with default GET.
- Evidence (backend): `server/app/api/auth.py:34` is `@bp.post("/auth/logout")`.

3. Auth bootstrap/hydration endpoints are stale.
- Impact: app init flow can fail before protected routes load.
- Evidence (client):
  - `src/context/AuthContext.jsx:13` uses `/api/auth/hydrate_user` (not present on backend).
  - `src/context/AuthContext.jsx:34` uses `/api/bootstrap/status` (not present on backend).
- Evidence (backend):
  - `server/app/api/auth.py:41` exposes `/api/auth/me`.
  - `server/app/api/bootstrap.py:36` and `server/app/api/bootstrap.py:45` expose GET/POST at `/api/bootstrap` (no `/status` suffix).

4. Bootstrap payload shape mismatches backend contract.
- Impact: bootstrap POST can fail validation even when endpoint is correct.
- Evidence (client):
  - `src/routes/initialize/Bootstrap.jsx:34` sends `admin` key.
  - `src/routes/initialize/Bootstrap.jsx:45` sends `department` but no `location.current_tax_rate`.
- Evidence (backend):
  - `server/app/api/bootstrap.py:80` loads `data["location"]`.
  - `server/app/api/bootstrap.py:81` loads `data["user"]` (not `admin`).
  - `server/app/api/bootstrap.py:95` expects `location_data["current_tax_rate"]`.

5. Active ticket page (`TicketTest`) does not match current ticket schema.
- Impact: ticket create requests will fail backend validation.
- Evidence (client):
  - Endpoint: `src/routes/home/homepages/ticket/TicketTest.jsx:220` (`/api/create/ticket`).
  - Payload fields:
    - `date` used instead of `ticket_date` at `src/routes/home/homepages/ticket/TicketTest.jsx:230`.
    - `category_id` used instead of `sales_category_id` at `src/routes/home/homepages/ticket/TicketTest.jsx:42`.
    - `payment_type` used instead of `payment_type_id` at `src/routes/home/homepages/ticket/TicketTest.jsx:51`.
    - missing `transaction_type` in request body (`src/routes/home/homepages/ticket/TicketTest.jsx:229`-`234`).
- Evidence (backend):
  - `server/app/schemas/ticket.py:14` (`ticket_date`)
  - `server/app/schemas/ticket.py:19` (`transaction_type` required)
  - `server/app/core/ticket_crud.py:101` (`sales_category_id`)
  - `server/app/core/ticket_crud.py:117` (`payment_type_id`)

## High Findings

1. Home route currently uses test pages, not primary pages.
- Impact: production path is tied to experimental implementations with legacy API usage.
- Evidence:
  - `src/routes/home/Home.jsx:9`
  - `src/routes/home/Home.jsx:10`
  - `src/routes/home/Home.jsx:19`
  - `src/routes/home/Home.jsx:21`

2. `TicketTest` contains a broken state update function.
- Impact: if invoked, this will throw due invalid array expression (`tenders` referenced during declaration).
- Evidence: `src/routes/home/homepages/ticket/TicketTest.jsx:168` (`const tenders = [...prev, tenders];`).

3. Registration flow is pointed at removed auth route.
- Impact: user creation via UI will fail.
- Evidence (client): `src/routes/auth/register/Register.jsx:35` uses `/api/auth/register`.
- Evidence (backend): user creation is resource CRUD under `users` (`server/app/api/user.py:24`), and backend handoff states create-user is admin-only.

## Medium Findings

1. Vite proxy config has reliability gaps for backend connectivity.
- Impact: local startup can silently run with undefined proxy target; lint already flags env handling.
- Evidence:
  - `vite.config.js:4` declares `process.env.SERVER_URL` (unused and lint error).
  - `vite.config.js:25` uses `target: env.SERVER_URL` with no guard/fallback.
- Recommendation: fail fast if `SERVER_URL`/`VITE_SERVER_URL` is missing, and normalize on one env key.

2. Lint baseline is currently very noisy (91 problems), which will hide real regressions while migrating routes.
- Evidence: `npm run lint` returns `89 errors, 2 warnings`.
- Key hotspots:
  - `src/routes/home/homepages/ticket/TicketTest.jsx`
  - `src/routes/home/homepages/search/Search.jsx`
  - `src/routes/home/homepages/search/SearchTest.jsx`
  - `src/routes/settings/settingspages/*`
  - `src/context/*`

## Notes For Next Pass

- Priority order to unblock client/backend integration:
1. Replace auth/bootstrap endpoints and methods first (`AuthContext`, `RootLayout`, `Bootstrap`, `Register`).
2. Introduce one centralized API client (single route map + method helpers) and migrate all legacy `/api/read|create|update|delete` usage.
3. Decide single ticket implementation (v5 target), then remove or fully gate the inactive variant.
4. Align ticket payload to backend schema (`ticket_date`, `transaction_type`, `sales_category_id`, `payment_type_id`).

<!-- ========================================================= -->
<!-- CHANGES MADE ON 02/09/2026 -->
<!-- ========================================================= -->

## Changes Made On 02/09/2026

### Auth / Bootstrap
- Updated client auth hydration endpoint to `GET /api/auth/me`.
- Updated bootstrap status check to `GET /api/bootstrap`.
- Updated logout request to `POST /api/auth/logout` with credentials.
- Updated bootstrap payload shape to use `user` (not `admin`) and include `location.current_tax_rate`.

### API Utility Standardization (`src/utils/api.jsx`)
- Added shared request helpers for consistent JSON/error handling.
- Added generic helpers:
  - `list(resource)`
  - `getById(resource, id)`
- Kept compatibility wrappers (`UserList`, `DepartmentList`, `LocationList`, `CategoriesList`, `PaymentTypeList`) mapped to the new generic API calls.

### Money Input Behavior
- Updated `MoneyField` behavior to avoid disruptive mid-typing reformatting.
- Confirmed monetary flow remains cents-based for backend payloads.

### Ticket Flow (Primary Implementation)
- Promoted `Ticket.jsx` as active ticket entry page and switched Home import away from `TicketTest`.
- Refactored ticket submission to REST endpoint `POST /api/tickets`.
- Aligned payload to backend schema:
  - `ticket_date`
  - `transaction_type`
  - `sales_category_id`
  - `payment_type_id`
  - `line_items`
  - `tenders`
- Reintroduced live ticket summary math (subtotal, tax, total, paid, balance/change).
- Enforced tender/payment presence in submit gating.
- Added/adjusted tender UX controls and compact styling.

### Categories Settings Page
- Updated create calls to REST endpoints:
  - `POST /api/sales_categories`
  - `POST /api/payment_types`
  - `POST /api/departments`
- Fixed payload field to `taxable` for sales categories.
- Updated response handling to CRUD-engine response keys.
- Cleaned and compacted settings form styling.

### Search / Ticket Detail Workflow (`SearchTest`)
- Reworked search flow to:
  - find by ticket number
  - fetch expanded ticket detail via `GET /api/tickets/{id}?expand=true`
- Added add-transaction form with:
  - user/type/date
  - dynamic line items
  - dynamic tenders
  - submit to `POST /api/transactions`
- Added transaction delete via `DELETE /api/transactions/{id}`.
- Reorganized form into compact layout inside ticket details section (not oversized modal-like block).
- Added compact live summary block in add form:
  - subtotal
  - tax
  - total
  - paid
  - balance/change
- Improved transaction detail cards to render:
  - line items per transaction with sales category names
  - tenders per transaction with payment type labels
- Added visual separation between line-item and tender detail sections.
- Updated destructive action styles for row-level remove buttons.

### Backend Support Added For Standalone Transaction Create
- Implemented custom transaction create flow in `server/app/core/transaction_crud.py`.
- Wired `server/app/api/transaction.py` to use `TransactionCRUDEngine`.
- Updated `server/app/schemas/transaction.py` to support nested `line_items` + `tenders` for transaction creation.
- Verified backend syntax (`py_compile`) and frontend lint checks (`eslint`) for touched files.

<!-- ====================================================================== -->
<!-- ========================= READ-ONLY AUDIT 2026-02-10 ================== -->
<!-- ====== BACKEND SOURCE OF TRUTH VS FRONTEND CONTRACT FOLLOW-UP ========= -->
<!-- ====================================================================== -->

## Read-Only Audit (2026-02-10)

This section reflects a read-only pass only. No files were changed during this audit.

### Backend Source Of Truth

- Generic resource routes are defined in `server/app/core/resource.py`:
  - `GET /api/<resource>`
  - `GET /api/<resource>/<id>`
  - `POST /api/<resource>`
  - `PATCH /api/<resource>/<id>`
  - `DELETE /api/<resource>/<id>`
- Registered resources:
  - `users` via `server/app/api/user.py:24`
  - `locations` via `server/app/api/location.py:24`
  - `deductions` via `server/app/api/deduction.py:24`
  - `tickets` via `server/app/api/ticket.py:27`
  - `transactions` via `server/app/api/transaction.py:24`
- Auth/bootstrap:
  - `POST /api/auth/login` (`server/app/api/auth.py:16`)
  - `POST /api/auth/logout` (`server/app/api/auth.py:34`)
  - `GET /api/auth/me` (`server/app/api/auth.py:41`)
  - `GET/POST /api/bootstrap` (`server/app/api/__init__.py:24`, `server/app/api/bootstrap.py`)

### Frontend Areas Already Aligned

- `client/src/context/AuthContext.jsx:13` uses `/api/auth/me`.
- `client/src/context/AuthContext.jsx:34` uses `/api/bootstrap`.
- `client/src/layout/RootLayout.jsx:13` uses `POST /api/auth/logout`.
- `client/src/routes/home/homepages/ticket/Ticket.jsx:237` uses `POST /api/tickets`.
- `client/src/routes/home/homepages/search/SearchTest.jsx:58` uses `GET /api/tickets/{id}?expand=true`.
- `client/src/routes/home/homepages/search/SearchTest.jsx:194` and `:233` use `/api/transactions`.

### Active Frontend Mismatches

1. Register flow still points to removed auth endpoint.
- Evidence: `client/src/routes/auth/register/Register.jsx:35` uses `/api/auth/register`.
- Backend contract: `POST /api/users` (`server/app/api/user.py:24`).

2. Users settings still uses legacy user routes.
- Evidence:
  - `client/src/routes/settings/settingspages/users/Users.jsx:39`
  - `client/src/routes/settings/settingspages/users/Users.jsx:40`
  - `client/src/routes/auth/edit/EditUser.jsx:57`

3. Locations settings still uses legacy routes.
- Evidence:
  - `client/src/routes/settings/settingspages/locations/Locations.jsx:33`
  - `client/src/routes/settings/settingspages/locations/Locations.jsx:72`
  - `client/src/routes/settings/settingspages/locations/Locations.jsx:105`
  - `client/src/routes/settings/settingspages/locations/Locations.jsx:136`

4. Deductions page still uses legacy routes.
- Evidence:
  - `client/src/routes/home/homepages/deduction/Deduction.jsx:35`
  - `client/src/routes/home/homepages/deduction/Deduction.jsx:51`
  - `client/src/routes/home/homepages/deduction/Deduction.jsx:79`

5. Reports/ranking endpoints used by frontend are not present in backend.
- Evidence (frontend):
  - `client/src/routes/home/homepages/ranking/Ranking.jsx:38` (`/api/read/monthly_totals`)
  - `client/src/routes/home/homepages/report/Report.jsx:60` (`/api/reports/summary`)
  - `client/src/routes/reports/reportpages/run_reports/RunReports.jsx:88` (`/api/reports/summary`)
  - `client/src/routes/reports/reportpages/ticket_list/TicketList.jsx:44` (`/api/read/tickets?...`)
- Evidence (backend): no report/monthly_totals routes found under `server/app/api/*`; API registration list in `server/app/api/__init__.py` does not include a reports blueprint.

### Contract Constraints Confirmed

- User deletion is disabled by backend: `server/app/core/user_crud.py` (`delete` raises permission denied).
- User update schema does not include `location_id`: `server/app/schemas/user.py` (`UserUpdateSchema` fields).
- Location updates in canonical resource routing are `PATCH`, not `PUT`: `server/app/core/resource.py`.
