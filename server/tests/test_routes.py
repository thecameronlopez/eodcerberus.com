import pytest
from app.extensions import bcrypt, db
from app.models import Department, Location, User

LIST_ENDPOINTS = [
    "/api/departments",
    "/api/sales_categories",
    "/api/payment_types",
    "/api/locations",
    "/api/deductions",
    "/api/taxrates",
    "/api/line_items",
    "/api/tenders",
    "/api/line_item_tenders",
    "/api/transactions",
    "/api/tickets",
    "/api/sales_days",
    "/api/users",
]


def _login_admin(client):
    email = "routes_admin@example.com"
    password = "Password123!"

    user = db.session.query(User).filter_by(email=email).first()
    if not user:
        department = db.session.query(Department).filter_by(name="RoutesOps").first()
        if not department:
            department = Department(name="RoutesOps", active=True)

        location = db.session.query(Location).filter_by(code="routes_hq").first()
        if not location:
            location = Location(name="RoutesHQ", code="routes_hq", current_tax_rate=0.1)

        user = User(
            email=email,
            first_name="Routes",
            last_name="Admin",
            department=department,
            location=location,
            is_admin=True,
            password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
        )
        db.session.add_all([department, location, user])
        db.session.commit()

    resp = client.post(
        "/api/auth/login",
        json={"email": email, "password": password},
    )
    assert resp.status_code == 200


@pytest.mark.parametrize("path", LIST_ENDPOINTS)
def test_list_routes_return_json(client, path):
    _login_admin(client)
    resp = client.get(path)
    assert resp.is_json
    assert resp.status_code == 200
    payload = resp.get_json()
    assert payload.get("success") is True


def test_bootstrap_status_returns_json(client):
    resp = client.get("/api/bootstrap")
    assert resp.is_json
    assert resp.status_code == 200
    payload = resp.get_json()
    assert "bootstrapped" in payload


def test_not_found_returns_json(client):
    _login_admin(client)
    resp = client.get("/api/locations/9999")
    assert resp.is_json
    assert resp.status_code == 404
    payload = resp.get_json()
    assert payload.get("success") is False
    assert payload["error"]["code"] == "RESOURCE_404"
