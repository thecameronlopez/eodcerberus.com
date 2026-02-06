import pytest

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


@pytest.mark.parametrize("path", LIST_ENDPOINTS)
def test_list_routes_return_json(client, path):
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
    resp = client.get("/api/locations/9999")
    assert resp.is_json
    assert resp.status_code == 404
    payload = resp.get_json()
    assert payload.get("success") is False
    assert payload["error"]["code"] == "RESOURCE_404"
