## Model/Schema Consistency Observations

1. High: `TicketDetailSchema` defines fields that do not exist on `Ticket`.
   `server/app/schemas/ticket.py:57` (`line_items`) and `server/app/schemas/ticket.py:58` (`tenders`) expect attributes on `Ticket`, but `Ticket` only has `transactions` (`server/app/models/ticket.py:21`). This can cause dump-time attribute errors or always-empty fields unless custom attributes are injected elsewhere.

2. High: Ticket create schema uses `date`, while model/update use `ticket_date`.
   `server/app/schemas/ticket.py:13` defines `date`, but model field is `ticket_date` (`server/app/models/ticket.py:11`), and update schema also uses `ticket_date` (`server/app/schemas/ticket.py:72`). This is an inconsistent contract and can silently fall back to default model date if not remapped in endpoint logic.

3. High: User registration schema does not align with non-null FK requirements on `User`.
   Model requires `department_id` and `location_id` (`server/app/models/users.py:19`, `server/app/models/users.py:20`), but `UserRegistrySchema` exposes optional `department` and `location_code` instead (`server/app/schemas/user.py:23`, `server/app/schemas/user.py:25`). Without strict resolver logic, user creation can fail with DB integrity errors.

4. Medium: Line item create schema omits required model fields.
   Model requires non-null `taxable` and `taxability_source` (`server/app/models/line_item.py:17`, `server/app/models/line_item.py:18`), but `LineItemCreateSchema` only accepts `sales_category_id`, `unit_price`, `quantity` (`server/app/schemas/line_item.py:12`). If service code does not always compute/populate missing fields, inserts will fail.

5. Medium: Relationship pairing is asymmetric in two spots.
   `SalesCategory.line_items` declares `back_populates="sales_category"` (`server/app/models/lookups.py:13`), but `LineItem.sales_category` omits `back_populates` (`server/app/models/line_item.py:27`). Same pattern for `PaymentType.tenders` (`server/app/models/lookups.py:26`) vs `Tender.payment_type` (`server/app/models/tender.py:15`). This can lead to weaker bidirectional synchronization and mapper warnings.

6. Medium: Index name implies uniqueness but does not enforce it.
   `ix_one_open_day_per_user` in `server/app/models/sales_day.py:49` is a normal index, not unique, so it does not enforce "one open day per user".

### Assumptions To Validate

1. If API logic intentionally remaps `date -> ticket_date`, resolves `department/location_code -> FK ids`, and auto-derives line-item taxability fields, findings 2–4 may be mitigated in runtime flows.
2. A follow-up pass through API handlers can confirm which findings are runtime bugs vs intentional schema abstraction.

## New Pain Points (Timezone + Error Handling)

1. Remaining local-date defaults still use system/naive `today()` instead of business timezone helper.

- `server/app/api/bootstrap.py:99` uses `datetime.date.today()` for `TaxRate.effective_from`.
- `server/app/models/transactions.py:20` uses `DTdate.today` for `posted_at`.
- `server/app/models/deductions.py:14` uses `DTdate.today` for `date`.

2. `TicketCreateSchema.ticket_date` mixes `required=True` with `load_default=business_today`.

- `server/app/schemas/ticket.py:14` has contradictory semantics; default only applies when field is not required.

3. Error handling is not fully standardized to `AppError` subclasses.

- `server/app/api/bootstrap.py:73` and `server/app/api/bootstrap.py:85` return direct JSON error responses.
- `server/app/models/line_item.py:38` raises raw `ValueError`.
- `server/app/core/ticket_crud.py:141` catches broad `Exception` and re-raises.

4. Marshmallow validation is mapped to base `AppError` (400) instead of explicit validation class (422).

- `server/app/handlers/errors/__init__.py:18` wraps schema validation with `AppError(...)` and `code="SCHEMA_422"` but keeps default status behavior.

## New Pain Points (API/Core Review - User/Auth Focus)

1. `POST /api/users` is intended to be admin-only but current resource wiring does not enforce auth/admin.

- `server/app/core/resource.py:12` exposes generic create route.
- `server/app/api/user.py:24` wires `UserCRUDEngine` through generic resource registration.
- `server/app/core/user_crud.py:44` currently accepts caller-provided `is_admin`.

2. Bootstrap route should be dev-only but currently lacks explicit environment guard.

- `server/app/api/bootstrap.py` should be blocked when `FLASK_ENV` is production (and optionally protected by a feature/env flag).

3. Legacy login view config references a non-existent auth endpoint.

- `server/app/__init__.py:26` sets `login_manager.login_view = "api.auth.login"` but no auth blueprint is registered.

4. User create flow should return controlled conflict/validation errors for duplicate email instead of generic 500 behavior.

- `server/app/models/users.py:13` has unique email constraint.
- `server/app/core/user_crud.py:49` commits without conflict translation.
