import uuid
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from api.db.base import Base
from api.db.session import get_db
from api.auth import get_current_user
from api.main import app
from api.models import User


@pytest.fixture(scope="function")
def db():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def user1(db):
    user = User(id=uuid.uuid4(), supabase_id="user1-id", email="user1@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def user2(db):
    user = User(id=uuid.uuid4(), supabase_id="user2-id", email="user2@example.com")
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class UserClient:
    def __init__(self, db, user):
        self.db = db
        self.user = user

    def _setup(self):
        def override_get_db():
            try:
                yield self.db
            finally:
                pass

        def override_get_current_user():
            return self.user

        app.dependency_overrides[get_db] = override_get_db
        app.dependency_overrides[get_current_user] = override_get_current_user

    def get(self, url):
        self._setup()
        with TestClient(app) as client:
            return client.get(url)

    def post(self, url, json=None):
        self._setup()
        with TestClient(app) as client:
            return client.post(url, json=json)

    def put(self, url, json=None):
        self._setup()
        with TestClient(app) as client:
            return client.put(url, json=json)

    def delete(self, url):
        self._setup()
        with TestClient(app) as client:
            return client.delete(url)


def test_create_item(db, user1):
    client = UserClient(db, user1)

    ws = client.post("/workspaces/", json={"name": "Test Workspace"}).json()
    workspace_id = ws["id"]

    resp = client.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Test Item", "description": "Test Description"},
    )

    assert resp.status_code == 200
    item = resp.json()
    assert item["title"] == "Test Item"
    assert item["description"] == "Test Description"
    assert "id" in item

    app.dependency_overrides.clear()


def test_read_items(db, user1):
    client = UserClient(db, user1)

    ws = client.post("/workspaces/", json={"name": "Test Workspace"}).json()
    workspace_id = ws["id"]

    client.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Item 1", "description": "Desc 1"},
    )
    client.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Item 2", "description": "Desc 2"},
    )

    resp = client.get(f"/items/?workspace_id={workspace_id}")

    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    titles = [i["title"] for i in items]
    assert "Item 1" in titles
    assert "Item 2" in titles

    app.dependency_overrides.clear()


def test_update_item(db, user1):
    client = UserClient(db, user1)

    ws = client.post("/workspaces/", json={"name": "Test Workspace"}).json()
    workspace_id = ws["id"]

    item = client.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Original Title", "description": "Original Desc"},
    ).json()
    item_id = item["id"]

    resp = client.put(
        f"/items/{item_id}",
        json={"title": "Updated Title", "description": "Updated Desc"},
    )

    assert resp.status_code == 200
    updated = resp.json()
    assert updated["title"] == "Updated Title"
    assert updated["description"] == "Updated Desc"

    fetched = client.get(f"/items/{item_id}").json()
    assert fetched["title"] == "Updated Title"

    app.dependency_overrides.clear()


def test_delete_item(db, user1):
    client = UserClient(db, user1)

    ws = client.post("/workspaces/", json={"name": "Test Workspace"}).json()
    workspace_id = ws["id"]

    item = client.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "To Delete", "description": "Will be deleted"},
    ).json()
    item_id = item["id"]

    items_before = client.get(f"/items/?workspace_id={workspace_id}").json()
    assert len(items_before) == 1

    resp = client.delete(f"/items/{item_id}")
    assert resp.status_code == 200
    assert resp.json()["ok"] is True

    items_after = client.get(f"/items/?workspace_id={workspace_id}").json()
    assert len(items_after) == 0

    app.dependency_overrides.clear()


def test_item_access_denied_without_workspace_membership(db, user1, user2):
    client1 = UserClient(db, user1)
    client2 = UserClient(db, user2)

    ws = client1.post("/workspaces/", json={"name": "Private Workspace"}).json()
    workspace_id = ws["id"]

    item = client1.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Private Item", "description": "Secret"},
    ).json()
    item_id = item["id"]

    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 403

    resp = client2.get(f"/items/{item_id}")
    assert resp.status_code == 403

    resp = client2.put(
        f"/items/{item_id}",
        json={"title": "Hacked", "description": "Hacked"},
    )
    assert resp.status_code == 403

    resp = client2.delete(f"/items/{item_id}")
    assert resp.status_code == 403

    app.dependency_overrides.clear()


def test_shared_workspace_item_access(db, user1, user2):
    client1 = UserClient(db, user1)
    client2 = UserClient(db, user2)

    ws = client1.post("/workspaces/", json={"name": "Shared Workspace"}).json()
    workspace_id = ws["id"]

    item = client1.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Shared Item", "description": "Visible to members"},
    ).json()

    client1.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "user2@example.com"},
    )

    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 1
    assert items[0]["title"] == "Shared Item"

    new_item = client2.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "User2 Item", "description": "Added by member"},
    ).json()
    assert new_item["title"] == "User2 Item"

    resp = client2.put(
        f"/items/{item['id']}",
        json={"title": "Updated by User2", "description": "Modified"},
    )
    assert resp.status_code == 200

    all_items = client1.get(f"/items/?workspace_id={workspace_id}").json()
    assert len(all_items) == 2

    app.dependency_overrides.clear()

