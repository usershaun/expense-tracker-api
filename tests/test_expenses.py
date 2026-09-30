def make_category(client, name="Food"):
    return client.post("/categories", json={"name": name}).json()


def expense_payload(category_id, **overrides):
    payload = {
        "amount": "12.50",
        "description": "Lunch",
        "spent_on": "2026-09-30",
        "category_id": category_id,
    }
    payload.update(overrides)
    return payload


def test_create_expense(client):
    category = make_category(client)

    response = client.post("/expenses", json=expense_payload(category["id"]))

    assert response.status_code == 201
    assert response.json() == {
        "id": 1,
        "amount": "12.50",
        "description": "Lunch",
        "spent_on": "2026-09-30",
        "category_id": category["id"],
    }


def test_create_expense_with_unknown_category_returns_404(client):
    response = client.post("/expenses", json=expense_payload(999))

    assert response.status_code == 404


def test_create_expense_with_zero_amount_returns_422(client):
    category = make_category(client)

    response = client.post(
        "/expenses", json=expense_payload(category["id"], amount="0")
    )

    assert response.status_code == 422


def test_create_expense_with_too_many_decimals_returns_422(client):
    category = make_category(client)

    response = client.post(
        "/expenses", json=expense_payload(category["id"], amount="12.505")
    )

    assert response.status_code == 422


def test_delete_category_in_use_returns_409(client):
    category = make_category(client)
    client.post("/expenses", json=expense_payload(category["id"]))

    response = client.delete(f"/categories/{category['id']}")

    assert response.status_code == 409
    assert response.json() == {"detail": "Category is used by existing expenses"}

def test_get_expense(client):
    category = make_category(client)
    created = client.post("/expenses", json=expense_payload(category["id"])).json()

    response = client.get(f"/expenses/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_get_missing_expense_returns_404(client):
    response = client.get("/expenses/999")

    assert response.status_code == 404


def test_update_expense(client):
    category = make_category(client)
    other = make_category(client, name="Transport")
    created = client.post("/expenses", json=expense_payload(category["id"])).json()

    response = client.put(
        f"/expenses/{created['id']}",
        json=expense_payload(
            other["id"], amount="30.00", description="Taxi", spent_on="2026-09-29"
        ),
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": created["id"],
        "amount": "30.00",
        "description": "Taxi",
        "spent_on": "2026-09-29",
        "category_id": other["id"],
    }
    assert client.get(f"/expenses/{created['id']}").json() == response.json()


def test_update_missing_expense_returns_404(client):
    category = make_category(client)

    response = client.put("/expenses/999", json=expense_payload(category["id"]))

    assert response.status_code == 404


def test_update_expense_with_unknown_category_returns_404(client):
    category = make_category(client)
    created = client.post("/expenses", json=expense_payload(category["id"])).json()

    response = client.put(
        f"/expenses/{created['id']}", json=expense_payload(999)
    )

    assert response.status_code == 404