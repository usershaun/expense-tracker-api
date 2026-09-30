def test_create_category(client):
    response = client.post("/categories", json={"name": "Food"})

    assert response.status_code == 201
    assert response.json() == {"id": 1, "name": "Food"}


def test_create_duplicate_category_returns_409(client):
    client.post("/categories", json={"name": "Food"})

    response = client.post("/categories", json={"name": "Food"})

    assert response.status_code == 409
    assert response.json() == {"detail": "Category already exists"}


def test_create_category_with_blank_name_returns_422(client):
    response = client.post("/categories", json={"name": "   "})

    assert response.status_code == 422


def test_list_categories_empty(client):
    response = client.get("/categories")

    assert response.status_code == 200
    assert response.json() == []


def test_list_categories_sorted_by_name(client):
    client.post("/categories", json={"name": "Transport"})
    client.post("/categories", json={"name": "Food"})

    response = client.get("/categories")

    names = [category["name"] for category in response.json()]
    assert names == ["Food", "Transport"]


def test_delete_category(client):
    created = client.post("/categories", json={"name": "Food"}).json()

    response = client.delete(f"/categories/{created['id']}")

    assert response.status_code == 204
    assert client.get("/categories").json() == []


def test_delete_missing_category_returns_404(client):
    response = client.delete("/categories/999")

    assert response.status_code == 404