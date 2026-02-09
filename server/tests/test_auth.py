from app.extensions import bcrypt, db
from app.models import Department, Location, User


def _seed_user(email="admin@example.com", password="Password123!"):
    key = email.split("@", 1)[0].replace(".", "_")
    department = Department(name=f"Ops_{key}", active=True)
    location = Location(name=f"HQ_{key}", code=f"hq_{key}", current_tax_rate=0.1)
    user = User(
        email=email,
        first_name="Admin",
        last_name="User",
        department=department,
        location=location,
        is_admin=True,
        password_hash=bcrypt.generate_password_hash(password).decode("utf-8"),
    )
    db.session.add_all([department, location, user])
    db.session.commit()
    return user


def test_login_sets_session_and_me_returns_user(client):
    _seed_user()

    login_resp = client.post(
        "/api/auth/login",
        json={"email": "admin@example.com", "password": "Password123!"},
    )
    assert login_resp.status_code == 200
    assert login_resp.is_json
    login_payload = login_resp.get_json()
    assert login_payload["success"] is True
    assert login_payload["user"]["email"] == "admin@example.com"

    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 200
    assert me_resp.is_json
    me_payload = me_resp.get_json()
    assert me_payload["success"] is True
    assert me_payload["user"]["email"] == "admin@example.com"


def test_login_with_bad_credentials_returns_error(client):
    _seed_user(email="staff@example.com", password="GoodPass123!")

    resp = client.post(
        "/api/auth/login",
        json={"email": "staff@example.com", "password": "WrongPass123!"},
    )
    assert resp.status_code == 403
    assert resp.is_json
    payload = resp.get_json()
    assert payload["success"] is False


def test_logout_clears_session(client):
    _seed_user(email="logout@example.com", password="Password123!")
    client.post(
        "/api/auth/login",
        json={"email": "logout@example.com", "password": "Password123!"},
    )

    logout_resp = client.post("/api/auth/logout")
    assert logout_resp.status_code == 200

    me_resp = client.get("/api/auth/me")
    assert me_resp.status_code == 403
    assert me_resp.is_json
