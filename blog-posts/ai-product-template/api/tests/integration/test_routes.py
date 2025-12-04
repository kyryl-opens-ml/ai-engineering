from tests.conftest import TEST_USER_ID

def test_create_item(client):
    response = client.post(
        "/items/",
        json={"title": "Integration Item", "description": "Integration Desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Integration Item"
    assert data["user_id"] == TEST_USER_ID
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

def test_items_are_user_scoped(client, db_session):
    from api.models.item import Item
    other_user_item = Item(user_id="other-user", title="Other Item", description="Not mine")
    db_session.add(other_user_item)
    db_session.commit()

    client.post("/items/", json={"title": "My Item"})

    response = client.get("/items/")
    data = response.json()
    assert len(data) == 1
    assert data[0]["title"] == "My Item"
    assert data[0]["user_id"] == TEST_USER_ID

