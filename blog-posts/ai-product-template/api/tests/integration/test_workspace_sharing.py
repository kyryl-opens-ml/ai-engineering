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

    def delete(self, url):
        self._setup()
        with TestClient(app) as client:
            return client.delete(url)


def test_workspace_sharing_scenario(db, user1, user2):
    """
    Scenario:
    1. User1 creates a workspace and adds items
    2. User2 cannot see items (no access)
    3. User1 adds User2 to workspace
    4. User2 can now see items
    """
    client1 = UserClient(db, user1)
    client2 = UserClient(db, user2)

    # User1 creates a workspace
    resp = client1.post("/workspaces/", json={"name": "User1 Workspace"})
    assert resp.status_code == 200
    workspace = resp.json()
    workspace_id = workspace["id"]
    assert workspace["role"] == "owner"

    # User1 creates items in the workspace
    resp = client1.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Item 1", "description": "First item"},
    )
    assert resp.status_code == 200

    resp = client1.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Item 2", "description": "Second item"},
    )
    assert resp.status_code == 200

    # User1 can see items
    resp = client1.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2

    # User2 cannot see the workspace (no access)
    resp = client2.get(f"/workspaces/{workspace_id}")
    assert resp.status_code == 403

    # User2 cannot see items (no access)
    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 403

    # User1 adds User2 to the workspace
    resp = client1.post(
        f"/workspaces/{workspace_id}/members",
        json={"email": "user2@example.com"},
    )
    assert resp.status_code == 200
    member = resp.json()
    assert member["role"] == "member"

    # User2 can now see the workspace
    resp = client2.get(f"/workspaces/{workspace_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "User1 Workspace"

    # User2 can now see items
    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert resp.status_code == 200
    items = resp.json()
    assert len(items) == 2
    assert items[0]["title"] in ["Item 1", "Item 2"]

    # User2 can also create items in the shared workspace
    resp = client2.post(
        f"/items/?workspace_id={workspace_id}",
        json={"title": "Item 3 by User2", "description": "Added by member"},
    )
    assert resp.status_code == 200

    # Both users see all 3 items now
    resp = client1.get(f"/items/?workspace_id={workspace_id}")
    assert len(resp.json()) == 3

    resp = client2.get(f"/items/?workspace_id={workspace_id}")
    assert len(resp.json()) == 3

    # Cleanup
    app.dependency_overrides.clear()
