from pydantic import BaseModel
from sqlalchemy import Column, Integer, String

from api.db.base import Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)


class ItemCreate(BaseModel):
    title: str
    description: str | None = None


class ItemRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    title: str
    description: str | None = None
