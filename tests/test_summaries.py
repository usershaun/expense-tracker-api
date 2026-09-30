def make_category(client, name):
    return client.post("/categories", json={"name": name}).json()


def add_expense(client, category_id, amount, spent_on):
    client.post(
        "/expenses",
        json={
            "amount": amount,
            "description": "test",
            "spent_on": spent_on,
            "category_id": category_id,
        },
    )


def test_monthly_summary(client):
    food = make_category(client, "Food")
    transport = make_category(client, "Transport")
    add_expense(client, food["id"], "10.10", "2026-09-05")
    add_expense(client, food["id"], "20.20", "2026-09-20")
    add_expense(client, transport["id"], "5.00", "2026-09-10")

    response = client.get("/summaries/monthly?year=2026&month=9")

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == "35.30"
    assert body["count"] == 3
    assert [c["category_name"] for c in body["by_category"]] == ["Food", "Transport"]
    assert body["by_category"][0]["total"] == "30.30"
    assert body["by_category"][0]["count"] == 2


def test_monthly_summary_for_empty_month(client):
    response = client.get("/summaries/monthly?year=2026&month=9")

    assert response.status_code == 200
    assert response.json() == {
        "year": 2026,
        "month": 9,
        "total": "0.00",
        "count": 0,
        "by_category": [],
    }


def test_monthly_summary_includes_first_and_last_day_only(client):
    food = make_category(client, "Food")
    add_expense(client, food["id"], "1.00", "2026-08-31")
    add_expense(client, food["id"], "2.00", "2026-09-01")
    add_expense(client, food["id"], "4.00", "2026-09-30")
    add_expense(client, food["id"], "8.00", "2026-10-01")

    response = client.get("/summaries/monthly?year=2026&month=9")

    assert response.json()["total"] == "6.00"


def test_monthly_summary_with_invalid_month_returns_422(client):
    assert client.get("/summaries/monthly?year=2026&month=13").status_code == 422
    assert client.get("/summaries/monthly?year=2026&month=0").status_code == 422