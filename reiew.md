# Server High-Level Overview

Date: 2026-02-09
Scope: `server/` full read audit
Excluded as requested: `server/migrations/`, `server/logs/`, `**/__pycache__/`

## Architecture Summary

- Backend is a Flask monolith with clear module boundaries:
- `app/models`: SQLAlchemy ORM entities for ticketing, transactions, tenders, allocations, users, and lookups.
- `app/schemas`: Marshmallow request/response contracts layered over models.
- `app/core`: generic CRUD engine plus custom flows (`UserCRUDEngine`, `TicketCRUDEngine`).
- `app/api`: mostly thin route wiring via `register_resource`; `bootstrap.py` is the only endpoint with substantial custom flow.
- `app/handlers/errors`: centralized error typing and JSON formatting with global Flask handlers.
- `app/services`: business logic helpers (allocation engine).
- `app/utils`: date/time, response, and transaction-finalization utilities.

## What Looks Good

- Consistent Flask app factory setup in `server/app/__init__.py`.
- Domain model shape is coherent for ticket -> transaction -> line_item/tender -> allocation.
- Error handling pattern has improved:
- Marshmallow validation now maps to app validation errors with 422 semantics.
- Resource/domain errors are standardized through `AppError` subclasses.
- Timezone strategy has materially improved:
- Business-local date helper exists (`app/utils/timezone.py`).
- Key business date fields now use `business_today`.
- Sales day/opened-at comparison in ticket creation converts UTC timestamp to business-local date before comparing.
- User creation hardening improved:
- `POST /api/users` now admin-gated via `create_admin_only=True`.
- Duplicate email collisions are translated to a conflict error.

## Key Risks / Gaps (High-Level)

- Auth/login flow is still incomplete in current source:
- `UserLoginSchema` exists, but there is no implemented login endpoint in `app/api`.
- No `login_user`/password-check route found in `app/`.
- Most CRUD endpoints are still open by default:
- Only user-create is explicitly admin-guarded in route registration.
- Other create/update/delete routes currently have no route-level auth guard.
- Bootstrap route is now production-blocked, but still uses hardcoded boot payload and credentials in code for dev flow.
- Commit/rollback robustness is uneven:
- `TicketCRUDEngine` and `UserCRUDEngine` now handle commit failures more safely.
- Generic `CRUDEngine` still commits directly without rollback wrapper.
- Data integrity semantics still contain one known mismatch:
- `sales_days` index `ix_one_open_day_per_user` is non-unique despite name implying uniqueness.

## Configuration / Ops Notes

- `.env` contains plaintext secrets (including DB credentials); this is acceptable for local dev but operationally sensitive.
- `config.py` expects `SQLALCHEMY_ECHO`, while `.env` currently defines `SQL_ALCHEMY_ECHO` (underscore mismatch), so SQL echo config may not behave as intended.
- `server/restart_db.py` is a full destructive reset utility (drops all metadata/tables).
- `server/instance/test.db` is present in tree, indicating a local SQLite artifact inside the repo path.

## Testing Posture

- Current tests are mostly route smoke tests (`tests/test_routes.py`) plus fixture setup.
- Coverage is thin for critical business paths:
- no explicit tests for user creation permissions/role assignment constraints.
- no explicit tests for duplicate-email conflict behavior.
- no explicit tests for timezone rollover/local-midnight behavior in ticket flow.
- no explicit tests for allocation math edge cases (rounding, partial tenders, non-taxable mixes).

## Suggested Priorities (Order)

1. Implement explicit auth endpoints/session flow (login/logout/me) and wire password verification.
2. Apply route-level authorization policy across non-public CRUD endpoints, not just users.
3. Add regression tests for user-create authorization, duplicate-email conflict, and ticket date rollover around local midnight.
4. Add rollback/error translation consistency to generic `CRUDEngine` write paths.
5. Decide whether bootstrap should remain hardcoded dev-only or move to one-time setup driven by request payload/env flag.
6. Align environment variable naming for SQL echo and consider secret-management hardening for non-dev environments.

<!-- ================================================================================================= -->
<!-- ======================== NEW REVIEW AFTER APPLYING OLD FIXES ==================================== -->
<!-- ================================================================================================= -->

## New Review After Applying Old Fixes

Date: 2026-02-09  
Scope: `server/` full pass after recent fixes  
Excluded: `server/migrations/`, `server/logs/`, `**/__pycache__/`

## What Is Now Fixed

- Auth/session flow now exists and is wired:
- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` in `server/app/api/auth.py`.
- Flask-Login unauthorized handling now returns structured API errors via `PermissionDenied`.

- CRUD routes are now auth-gated by default:
- `register_resource(..., require_auth=True)` enforces authenticated access for all generated CRUD routes.
- User create remains admin-only through `create_admin_only=True`.

- Generic CRUD engine now has safer write behavior:
- Rollback on failed commits.
- `IntegrityError` translated to `ConflictError` instead of falling through to generic 500.

- Timezone handling is stricter:
- `business_timezone()` now fails fast when timezone data is unavailable instead of silently falling back to UTC.
- `create_app()` validates timezone at startup.
- `tzdata` dependency is in `server/requirements.txt`.

- Bootstrap endpoint behavior improved:
- Dev-only guard is enforced (`FLASK_ENV == "production"` is blocked).
- Request payload override is supported, with fallback to local default payload.

- Test coverage improved:
- Added auth session tests.
- Added authz + duplicate-email + ticket business-date rollover regression tests.
- Current suite status observed in this session: `22 passed`.

## Remaining Gaps / Risks

- Production config enforcement is present but not guaranteed to be used by default runtime path.
- `server/wsgi.py` calls `create_app()` with default `Config`, not `ProductionConfig`.
- Result: strict env validation in `ProductionConfig.validate()` can be bypassed unless deployment explicitly passes/loads `ProductionConfig`.

- Authorization depth is still coarse for non-admin users.
- All CRUD routes require authentication, but most write operations are not role/ownership constrained.
- Any authenticated user can currently create/update/delete many resources (except `POST /api/users`).

- Bootstrap route remains unauthenticated in non-production environments.
- This is intentional for dev workflow, but if a non-prod environment is internet-exposed, it is still a high-risk control point.

- Hardcoded bootstrap default credentials are still present in code (`boot_data` in `server/app/api/bootstrap.py`).
- This is useful for local reset convenience, but should never be used outside isolated local/dev scenarios.

- Minor code hygiene issue:
- `taxrate_create_schema` is imported in `server/app/api/bootstrap.py` but unused.

- Operational hygiene:
- `server/instance/test.db` remains inside repo path.
- `server/restart_db.py` is intentionally destructive and should remain tightly controlled.

## Recommended Next Moves

1. Make production config selection explicit at startup (`wsgi.py`) so `ProductionConfig` validation is always enforced in prod.
2. Add role/permission policy beyond "authenticated" for sensitive write paths (at least admin-only for master/lookup writes).
3. Keep bootstrap dev-only and optionally require an extra flag/token even in dev/staging.
4. Remove hardcoded dev credentials from source or move them to local-only environment variables.
