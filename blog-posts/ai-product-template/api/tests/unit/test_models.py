from api.models.item import Item

def test_item_model_instantiation():
    item = Item(user_id="user-123", title="Test", description="Desc")
    assert item.user_id == "user-123"
    assert item.title == "Test"
    assert item.description == "Desc"

