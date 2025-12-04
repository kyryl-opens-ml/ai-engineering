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
    # Check if our item is in the list
    found = any(item["title"] == "Item 1" for item in data)
    assert found

