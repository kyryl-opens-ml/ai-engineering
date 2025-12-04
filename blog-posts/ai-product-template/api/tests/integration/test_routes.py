def test_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the API"}


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "version" in data


def test_create_item(client):
    response = client.post(
        "/items/",
        json={"title": "Integration Item", "description": "Integration Desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Integration Item"
    assert "id" in data


def test_read_items(client):
    client.post(
        "/items/",
        json={"title": "Item 1", "description": "Desc 1"},
    )
    response = client.get("/items/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found = any(item["title"] == "Item 1" for item in data)
    assert found


def test_read_item(client):
    create_response = client.post(
        "/items/",
        json={"title": "Single Item", "description": "Single Desc"},
    )
    item_id = create_response.json()["id"]
    response = client.get(f"/items/{item_id}")
    assert response.status_code == 200
    assert response.json()["title"] == "Single Item"


def test_read_item_not_found(client):
    response = client.get("/items/9999")
    assert response.status_code == 404
