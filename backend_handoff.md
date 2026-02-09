# Backend Handoff (Session Summary)

Date: 2026-02-09
Project: `eodcerberus.com` backend (`server/`)

## Final State

- Backend auth/session flow exists and is working.
- CRUD routes are auth-required by default.
- Master/lookup write routes are admin-only.
- User policy:
  - create user: admin-only
  - update user: self-update allowed, admin can update any user
  - delete user: disabled for everyone
- Timezone logic is strict and fail-fast (no silent UTC fallback).
- Generic CRUD writes now rollback on failure and translate integrity conflicts to 409.
- Relationship pairing asymmetry fixed for `SalesCategory <-> LineItem` and `PaymentType <-> Tender`.
- Enforced one-open-sales-day-per-user behavior at model level.
- Full test suite passes: `26 passed`.

## Key Files Changed

- Auth/session:
  - `server/app/api/auth.py`
  - `server/app/api/__init__.py`
  - `server/app/__init__.py`

- Authorization policy:
  - `server/app/core/resource.py`
  - `server/app/api/department.py`
  - `server/app/api/sales_category.py`
  - `server/app/api/payment_type.py`
  - `server/app/api/location.py`
  - `server/app/api/taxrate.py`
  - `server/app/api/user.py`

- User CRUD policy:
  - `server/app/core/user_crud.py`

- CRUD conflict/rollback:
  - `server/app/core/crud_engine.py`

- Ticket/sales-day consistency:
  - `server/app/core/ticket_crud.py`
  - `server/app/models/sales_day.py`

- Timezone/config hardening:
  - `server/app/utils/timezone.py`
  - `server/config.py`
  - `server/wsgi.py`
  - `server/requirements.txt` (includes `tzdata`)

- Bootstrap updates (dev flow):
  - `server/app/api/bootstrap.py`

- Relationship symmetry:
  - `server/app/models/line_item.py`
  - `server/app/models/tender.py`

- Cleanup:
  - deleted `server/app/utils/db.py`
  - unused import cleanup in multiple files

- Tests:
  - `server/tests/test_auth.py`
  - `server/tests/test_authz_and_ticket_timezone.py`
  - `server/tests/test_routes.py`
  - `server/tests/conftest.py`

## Intentional Decisions

- Bootstrap remains dev-only and is planned to be removed/ignored in production.
- Hardcoded bootstrap fallback payload is intentionally retained for local reset convenience.
- Production secret validation is enforced by config selection in `wsgi.py`.

## How To Resume In A New Session

1. Ask assistant to read this file first:
   - `backend_handoff.md`
2. If working on backend, also load:
   - `server/codex_summ.md`
   - `reiew.md` (historical reviews)
3. Run tests in project venv:
   - `D:\python\venvs\cerberus\Scripts\Activate.ps1`
   - `cd D:\repos\eodcerberus.com\server`
   - `python -m pytest -q`
