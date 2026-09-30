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