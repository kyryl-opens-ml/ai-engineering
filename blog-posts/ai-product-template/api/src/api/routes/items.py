import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.auth import get_current_user
from api.models.user import User
from api.models.item import Item, ItemCreate, ItemRead
from api.models.workspace import Workspace
from api.models.workspace_member import WorkspaceMember

router = APIRouter()


def check_workspace_access(
    db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID
) -> bool:
    if (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.owner_id == user_id)
        .first()
    ):
        return True
    if (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    ):
        return True
    return False


@router.post("/", response_model=ItemRead)
def create_item(
    workspace_id: uuid.UUID,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not check_workspace_access(db, workspace_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    db_item = Item(
        workspace_id=workspace_id, title=item.title, description=item.description
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


@router.get("/", response_model=list[ItemRead])
def read_items(
    workspace_id: uuid.UUID,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not check_workspace_access(db, workspace_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    items = (
        db.query(Item)
        .filter(Item.workspace_id == workspace_id)
        .offset(skip)
        .limit(limit)
        .all()
    )
    return items


@router.get("/{item_id}", response_model=ItemRead)
def read_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if not check_workspace_access(db, db_item.workspace_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    return db_item


@router.put("/{item_id}", response_model=ItemRead)
def update_item(
    item_id: uuid.UUID,
    item: ItemCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if not check_workspace_access(db, db_item.workspace_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    db_item.title = item.title
    db_item.description = item.description
    db.commit()
    db.refresh(db_item)
    return db_item


@router.delete("/{item_id}")
def delete_item(
    item_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_item = db.query(Item).filter(Item.id == item_id).first()
    if db_item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    if not check_workspace_access(db, db_item.workspace_id, current_user.id):
        raise HTTPException(status_code=403, detail="Access denied")
    db.delete(db_item)
    db.commit()
    return {"ok": True}
