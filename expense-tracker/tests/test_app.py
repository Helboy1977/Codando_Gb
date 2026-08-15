import pytest

from app import create_app, db


@pytest.fixture
def client():
    app = create_app(db_uri="sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
    with app.app_context():
        db.drop_all()


def test_index_page(client):
    res = client.get("/")
    assert res.status_code == 200


def test_list_expenses_empty(client):
    res = client.get("/api/expenses")
    assert res.status_code == 200
    assert res.get_json() == []


def test_create_expense(client):
    res = client.post("/api/expenses", json={
        "description": "Almoço",
        "amount": 25.5,
        "category": "Alimentação",
        "date": "2026-08-01",
    })
    assert res.status_code == 201
    body = res.get_json()
    assert body["description"] == "Almoço"
    assert body["amount"] == 25.5

    res = client.get("/api/expenses")
    assert len(res.get_json()) == 1


def test_create_expense_invalid_amount(client):
    res = client.post("/api/expenses", json={
        "description": "Almoço",
        "amount": "abc",
        "category": "Alimentação",
    })
    assert res.status_code == 400


def test_create_expense_invalid_category(client):
    res = client.post("/api/expenses", json={
        "description": "Almoço",
        "amount": 10,
        "category": "Inexistente",
    })
    assert res.status_code == 400


def test_delete_expense(client):
    create_res = client.post("/api/expenses", json={
        "description": "Cinema",
        "amount": 40,
        "category": "Lazer",
    })
    expense_id = create_res.get_json()["id"]

    delete_res = client.delete(f"/api/expenses/{expense_id}")
    assert delete_res.status_code == 204

    res = client.get("/api/expenses")
    assert res.get_json() == []


def test_delete_missing_expense(client):
    res = client.delete("/api/expenses/999")
    assert res.status_code == 404


def test_summary(client):
    client.post("/api/expenses", json={"description": "A", "amount": 10, "category": "Lazer"})
    client.post("/api/expenses", json={"description": "B", "amount": 20, "category": "Lazer"})
    client.post("/api/expenses", json={"description": "C", "amount": 5, "category": "Transporte"})

    res = client.get("/api/summary")
    body = res.get_json()
    assert body["total"] == 35
    assert body["by_category"] == {"Lazer": 30, "Transporte": 5}
