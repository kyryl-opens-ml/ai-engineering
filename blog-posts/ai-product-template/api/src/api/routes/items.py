from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.auth import get_current_user
from api.models.item import Item, ItemCreate, ItemRead

router = APIRouter()

@router.post("/", response_model=ItemRead)
def create_item(
    item: ItemCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    db_item = Item(user_id=user_id, title=item.title, description=item.description)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item

@router.get("/", response_model=list[ItemRead])
def read_items(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    items = db.query(Item).filter(Item.user_id == user_id).offset(skip).limit(limit).all()
    return items

@router.get("/{item_id}", response_model=ItemRead)
def read_item(
    item_id: int,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    db_item = db.query(Item).filter(Item.id == item_id, Item.user_id == user_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return db_item

