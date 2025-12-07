import uuid
from sqlalchemy import Column, String, ForeignKey
from pydantic import BaseModel, ConfigDict
from api.db.base import Base
from api.db.types import UUID



class Item(Base):
    __tablename__ = "items"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID, ForeignKey("workspaces.id"))
    title = Column(String, index=True)
    description = Column(String, nullable=True)


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    workspace_id: uuid.UUID
    title: str
    description: str | None = None
