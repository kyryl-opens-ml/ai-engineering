from api.models.item import Item

def test_item_model_instantiation():
    item = Item(title="Test", description="Desc")
    assert item.title == "Test"
    assert item.description == "Desc"

