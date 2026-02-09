from datetime import datetime, timezone
from uuid import uuid4

from app.extensions import bcrypt, db
from app.models import Department, Location, PaymentType, SalesCategory, SalesDay, User


def _mk(prefix: str) -> str:
    return f"{prefix}_{uuid4().hex[:8]}"


def _seed_admin():
    email = "authz_admin@example.com"
    password = "Password123!"
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        return user, password

    department = Department(name=_mk("dept"), active=True)
    location = Location(name=_mk("loc"), code=_mk("code"), current_tax_rate=0.1)
    user = User(
        email=email,
        first_name="Authz",
        last_name="Admin",
        department=department,
        location=location,
        is_admin=True,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add_all([department, location, user])
    db.session.commit()
    return user, password


def _seed_staff():
    email = "authz_staff@example.com"
    password = "Password123!"
    user = db.session.query(User).filter_by(email=email).first()
    if user:
        return user, password

    department = Department(name=_mk("dept"), active=True)
    location = Location(name=_mk("loc"), code=_mk("code"), current_tax_rate=0.1)
    user = User(
        email=email,
        first_name="Authz",
        last_name="Staff",
        department=department,
        location=location,
        is_admin=False,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add_all([department, location, user])
    db.session.commit()
    return user, password


def _login(client, email: str, password: str):
    resp = client.post("/api/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200


def _seed_user_create_context():
    department = Department(name=_mk("userdept"), active=True)
    location = Location(name=_mk("userloc"), code=_mk("usercode"), current_tax_rate=0.1)
    db.session.add_all([department, location])
    db.session.commit()
    return department, location


def test_users_create_requires_auth(client):
    department, location = _seed_user_create_context()
    payload = {
        "email": f"{_mk('user')}@example.com",
        "first_name": "New",
        "last_name": "User",
        "pw": "Password123!",
        "pw2": "Password123!",
        "department": department.name,
        "location_code": location.code,
        "is_admin": True,
    }
    resp = client.post("/api/users", json=payload)
    assert resp.status_code == 403


def test_users_create_requires_admin_role(client):
    staff, password = _seed_staff()
    _login(client, staff.email, password)

    department, location = _seed_user_create_context()
    payload = {
        "email": f"{_mk('user')}@example.com",
        "first_name": "New",
        "last_name": "User",
        "pw": "Password123!",
        "pw2": "Password123!",
        "department": department.name,
        "location_code": location.code,
        "is_admin": True,
    }
    resp = client.post("/api/users", json=payload)
    assert resp.status_code == 403


def test_users_create_duplicate_email_returns_conflict(client):
    admin, password = _seed_admin()
    _login(client, admin.email, password)

    department, location = _seed_user_create_context()
    email = f"{_mk('dup')}@example.com"
    payload = {
        "email": email,
        "first_name": "Dup",
        "last_name": "User",
        "pw": "Password123!",
        "pw2": "Password123!",
        "department": department.name,
        "location_code": location.code,
        "is_admin": False,
    }

    first = client.post("/api/users", json=payload)
    assert first.status_code == 201

    second = client.post("/api/users", json=payload)
    assert second.status_code == 409
    assert second.is_json
    assert second.get_json()["success"] is False


def test_users_update_allows_self_for_non_admin(client):
    staff, password = _seed_staff()
    _login(client, staff.email, password)

    resp = client.patch(f"/api/users/{staff.id}", json={"first_name": "Updated"})
    assert resp.status_code == 200
    assert resp.is_json
    assert resp.get_json()["success"] is True
    assert resp.get_json()["user"]["first_name"] == "Updated"


def test_users_update_blocks_non_admin_from_updating_others(client):
    staff, password = _seed_staff()
    admin, _ = _seed_admin()
    _login(client, staff.email, password)

    resp = client.patch(f"/api/users/{admin.id}", json={"first_name": "Nope"})
    assert resp.status_code == 403
    assert resp.is_json
    assert resp.get_json()["success"] is False


def test_users_delete_is_disabled_for_everyone(client):
    staff, password = _seed_staff()
    _login(client, staff.email, password)

    resp = client.delete(f"/api/users/{staff.id}")
    assert resp.status_code == 403
    assert resp.is_json
    assert resp.get_json()["success"] is False


def test_ticket_reuses_sales_day_by_business_date_rollover(client):
    admin, password = _seed_admin()
    _login(client, admin.email, password)

    location = admin.location
    user = admin

    category = SalesCategory(name=_mk("cat"), taxable=True, active=True)
    payment_type = PaymentType(name=_mk("pay"), taxable=False, active=True)
    db.session.add_all([category, payment_type])
    db.session.commit()

    # Use a timestamp that resolves to 2026-01-01 in both configured TZ and UTC fallback.
    existing_sales_day = SalesDay(
        user_id=user.id,
        location_id=location.id,
        opened_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        status="open",
    )
    db.session.add(existing_sales_day)
    db.session.commit()

    payload = {
        "ticket_number": int(uuid4().int % 1_000_000_000),
        "ticket_date": "2026-01-01",
        "user_id": user.id,
        "location_id": location.id,
        "transaction_type": "sale",
        "line_items": [{"sales_category_id": category.id, "unit_price": 1000, "quantity": 1}],
        "tenders": [{"payment_type_id": payment_type.id, "amount": 1000}],
    }
    resp = client.post("/api/tickets", json=payload)
    assert resp.status_code == 201
    assert resp.is_json

    ticket = resp.get_json()["ticket"]
    assert ticket["sales_day_id"] == existing_sales_day.id


def test_sales_day_create_conflicts_when_open_day_exists(client):
    email = f"{_mk('open_day_admin')}@example.com"
    password = "Password123!"
    department = Department(name=_mk("dept"), active=True)
    location = Location(name=_mk("loc"), code=_mk("code"), current_tax_rate=0.1)
    admin = User(
        email=email,
        first_name="Open",
        last_name="Day",
        department=department,
        location=location,
        is_admin=True,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add_all([department, location, admin])
    db.session.commit()

    _login(client, admin.email, password)

    existing_sales_day = SalesDay(
        user_id=admin.id,
        location_id=admin.location_id,
        opened_at=datetime(2026, 1, 1, 12, 0, tzinfo=timezone.utc),
        status="open",
    )
    db.session.add(existing_sales_day)
    db.session.commit()

    payload = {
        "user_id": admin.id,
        "location_id": admin.location_id,
        "starting_cash": 50000,
    }
    resp = client.post("/api/sales_days", json=payload)
    assert resp.status_code == 409
    assert resp.is_json
    assert resp.get_json()["success"] is False
