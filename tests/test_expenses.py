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


def test_delete_expense(client):
    category = make_category(client)
    created = client.post("/expenses", json=expense_payload(category["id"])).json()

    response = client.delete(f"/expenses/{created['id']}")

    assert response.status_code == 204
    assert client.get(f"/expenses/{created['id']}").status_code == 404


def test_delete_missing_expense_returns_404(client):
    response = client.delete("/expenses/999")

    assert response.status_code == 404

def test_list_expenses_empty(client):
    response = client.get("/expenses")

    assert response.status_code == 200
    assert response.json() == []


def test_list_expenses_newest_first(client):
    category = make_category(client)
    client.post(
        "/expenses", json=expense_payload(category["id"], spent_on="2026-09-01")
    )
    client.post(
        "/expenses", json=expense_payload(category["id"], spent_on="2026-09-20")
    )
    client.post(
        "/expenses", json=expense_payload(category["id"], spent_on="2026-09-10")
    )

    response = client.get("/expenses")

    dates = [expense["spent_on"] for expense in response.json()]
    assert dates == ["2026-09-20", "2026-09-10", "2026-09-01"]

def create_expenses_on(client, category_id, dates):
    for spent_on in dates:
        client.post(
            "/expenses", json=expense_payload(category_id, spent_on=spent_on)
        )


def test_list_expenses_filtered_by_date_range_is_inclusive(client):
    category = make_category(client)
    create_expenses_on(
        client,
        category["id"],
        ["2026-08-31", "2026-09-01", "2026-09-15", "2026-09-30", "2026-10-01"],
    )

    response = client.get("/expenses?start=2026-09-01&end=2026-09-30")

    dates = [expense["spent_on"] for expense in response.json()]
    assert dates == ["2026-09-30", "2026-09-15", "2026-09-01"]


def test_list_expenses_with_only_start(client):
    category = make_category(client)
    create_expenses_on(client, category["id"], ["2026-09-01", "2026-09-20"])

    response = client.get("/expenses?start=2026-09-10")

    dates = [expense["spent_on"] for expense in response.json()]
    assert dates == ["2026-09-20"]


def test_list_expenses_with_invalid_date_returns_422(client):
    response = client.get("/expenses?start=banana")

    assert response.status_code == 422

def test_list_expenses_filtered_by_category(client):
    food = make_category(client, name="Food")
    transport = make_category(client, name="Transport")
    client.post("/expenses", json=expense_payload(food["id"]))
    client.post("/expenses", json=expense_payload(transport["id"]))

    response = client.get(f"/expenses?category_id={transport['id']}")

    assert [e["category_id"] for e in response.json()] == [transport["id"]]


def test_list_expenses_combines_category_and_date_filters(client):
    food = make_category(client, name="Food")
    transport = make_category(client, name="Transport")
    client.post(
        "/expenses", json=expense_payload(food["id"], spent_on="2026-09-05")
    )
    client.post(
        "/expenses", json=expense_payload(food["id"], spent_on="2026-08-05")
    )
    client.post(
        "/expenses", json=expense_payload(transport["id"], spent_on="2026-09-05")
    )

    response = client.get(
        f"/expenses?category_id={food['id']}&start=2026-09-01&end=2026-09-30"
    )

    result = response.json()
    assert len(result) == 1
    assert result[0]["category_id"] == food["id"]
    assert result[0]["spent_on"] == "2026-09-05"


def test_list_expenses_with_unknown_category_returns_empty_list(client):
    response = client.get("/expenses?category_id=999")

    assert response.status_code == 200
    assert response.json() == []