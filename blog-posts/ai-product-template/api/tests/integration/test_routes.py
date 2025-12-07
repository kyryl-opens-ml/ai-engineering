def test_create_workspace(client):
    response = client.post("/workspaces/", json={"name": "Test Workspace"})
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Workspace"
    assert data["role"] == "owner"


def test_create_item(client):
    ws = client.post("/workspaces/", json={"name": "WS"}).json()
    response = client.post(
        f"/items/?workspace_id={ws['id']}",
        json={"title": "Integration Item", "description": "Integration Desc"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Integration Item"
    assert "id" in data


def test_read_items(client):
    ws = client.post("/workspaces/", json={"name": "WS"}).json()
    client.post(
        f"/items/?workspace_id={ws['id']}",
        json={"title": "Item 1", "description": "Desc 1"},
    )
    response = client.get(f"/items/?workspace_id={ws['id']}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    found = any(item["title"] == "Item 1" for item in data)
    assert found
