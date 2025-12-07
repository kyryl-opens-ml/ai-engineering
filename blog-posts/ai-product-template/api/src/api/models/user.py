import uuid
from sqlalchemy import Column, String
from pydantic import BaseModel, ConfigDict
from api.db.base import Base
from api.db.types import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    supabase_id = Column(String, unique=True, index=True)
    email = Column(String, nullable=True)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    email: str | None = None
