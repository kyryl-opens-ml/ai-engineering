from sqlalchemy import Column, Integer, String
from pydantic import BaseModel, ConfigDict
from api.db.base import Base

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String, nullable=True)

class ItemCreate(BaseModel):
    title: str
    description: str | None = None

class ItemRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: str
    title: str
    description: str | None = None

