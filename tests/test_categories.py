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