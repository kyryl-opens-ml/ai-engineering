import uuid
from api.models import Item, User, Workspace



def test_item_model_instantiation():
    ws_id = uuid.uuid4()
    item = Item(workspace_id=ws_id, title="Test", description="Desc")
    assert item.title == "Test"
    assert item.description == "Desc"


def test_user_model_instantiation():
    user = User(supabase_id="abc123", email="test@example.com")
    assert user.supabase_id == "abc123"


def test_workspace_model_instantiation():
    user_id = uuid.uuid4()
    workspace = Workspace(name="My Workspace", owner_id=user_id)
    assert workspace.name == "My Workspace"
