# eodcerberus.com/server Summary

Below is a full repo inspection summary of `D:\repos\eodcerberus.com\server`. I read all source files, migrations, and test code. I did not display `.env` contents for safety, but I confirmed it exists.

**Overview**

- Flask app with `create_app` factory, SQLAlchemy models, Marshmallow schemas, and CRUD endpoints.
- Core pattern: `CRUDEngine` + `register_resource` generates CRUD routes per model.
- Domain is POS-style ticketing: `Ticket`, `Transaction`, `LineItem`, `Tender`, `SalesDay`, and lookups (`SalesCategory`, `PaymentType`, `Department`).

**Runtime Entry**

- `wsgi.py` creates the app and runs it.
- There is a syntax error in `wsgi.py` (see “Critical findings”).

**Configuration**

- `config.py` sets DB URI, debug, CORS origins, and Redis session settings.
- Redis session settings are configured, but there is no Flask-Session integration, so those settings are currently unused.

**API Surface**
Blueprints are registered under `/api` in `app/api/__init__.py`.

- `/api/bootstrap` (GET/POST)
- `/api/departments`
- `/api/sales_categories`
- `/api/payment_types`
- `/api/locations`
- `/api/deductions`
- `/api/taxrates`
- `/api/line_items`
- `/api/tenders`
- `/api/line_item_tenders`
- `/api/transactions`
- `/api/tickets`
- `/api/sales_days`
- `/api/users`

All of these use `CRUDEngine` except `tickets`, which uses `TicketCRUDEngine`.

**Models**

- `User` has department and location FK, and relations to tickets, transactions, deductions, sales_days.
- `Ticket` has `transactions`, `sales_day`, and `user`.
- `Transaction` has `line_items`, `tenders`, and totals.
- `LineItem` has totals and tax fields; relations to `SalesCategory` and `LineItemTender` allocations.
- `Tender` references `PaymentType`.
- `SalesDay` tracks cash management and ticket list.
- `Deduction`, `TaxRate`, `Location`, lookups.

**Schemas**

- Marshmallow schemas for each model.
- Create schemas are plain `BaseSchema` (dicts).
- Update schemas are `SQLAlchemyAutoSchema` with `load_instance=True`.

**Services**

- `allocate_tender_to_line_items` creates `LineItemTender` allocations based on tender amount.

**Errors**

- Custom `AppError` with `error_response`.
- Marshmallow errors are wrapped into `ValidationError` response.

**Tests**

- `tests/test_routes.py` only checks list endpoints and bootstrap status. No mutation tests.

**Migrations**

- Alembic config exists.
- Migrations reference an `eod` table not present in models (likely legacy).

---

## Critical findings

1. **`wsgi.py` has a syntax error.**  
   `print(f"Starting {os.environ.get("APP_NAME", 'Cerberus')} ...")`  
   This will crash on startup due to nested double quotes.

2. **`CRUDEngine.create` is broken for most resources.**  
   It expects `create_schema.load()` to return a model instance.  
   But the create schemas are plain `BaseSchema` returning dicts, so `db.session.add(instance)` will throw.

3. **`/api/users` create is not usable as-is.**  
   It uses `user_register_schema` (dict), and does not hash the password. Even if it did, the `CRUDEngine` issue breaks it.

4. **`/api/bootstrap` hardcodes a password and ignores request data.**  
   `boot_data` has credentials and is always used; request payload is commented out. This is a security issue and blocks real bootstrap payloads.

---

## Major functional issues

1. **`TicketCRUDEngine` schema mismatch.**  
   `TicketCreateSchema` allows `user_id` to be optional, but `TicketCRUDEngine.create` does `data["user_id"]` unconditionally.  
   `tenders` is optional but later assumed present.

2. **`LineItem.paid_total` uses a non-existent relation.**  
   `LineItem` has `allocations`, not `tenders`.  
   `paid_total` and `remaining_total` will fail.

3. **`User.cash_total_for_date` references `posted_date`, but model has `posted_at`.**  
   This method will always error or return zero.

4. **`SalesDay.compute_expected_cash` compares `tender.payment_type == "CASH"`.**  
   `payment_type` is a relationship, so comparison to string will never be true.

5. **`TicketCRUDEngine` doesn’t validate `SalesCategory`/`PaymentType` existence.**  
   `db.session.get` may return `None`, but then the code uses `.id` immediately.

6. **`SalesDay` selection uses `user_id` only.**  
   `TicketCRUDEngine` will reuse the first sales day ever created for that user, regardless of status or date.

---

## Moderate issues / inconsistencies

- `CRUDEngine.list` pluralizes by adding `s` to class name.  
  `SalesCategory` becomes `salescategorys`.
- `SalesDayCloseSchema` has `closet_at` typo.
- Some schema comments and imports are duplicated or inconsistent.
- Alembic migrations reference `eod` table no longer modeled.

---

## Security notes

- Hardcoded admin credentials and email in `app/api/bootstrap.py`.
- No auth layer or login routes in repo. `login_manager.login_view` points to `api.auth.login`, but `auth.py` is missing.
- `.env` exists; not read here.

---

## Files referenced

- `wsgi.py`
- `config.py`
- `app/__init__.py`
- `app/logger.py`
- `app/core/crud_engine.py`
- `app/core/resource.py`
- `app/core/ticket_crud.py`
- `app/api/*.py`
- `app/models/*.py`
- `app/schemas/*.py`
- `app/services/allocations.py`
- `app/utils/*`
- `app/handlers/errors/*`
- `tests/*`
- `migrations/*`
