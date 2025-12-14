import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from api.db.base import Base
from api.db.types import UUID


class Workspace(Base):
    __tablename__ = "workspaces"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    name = Column(String, index=True)
    owner_id = Column(UUID, ForeignKey("users.id"))

    owner = relationship("User")
    members = relationship("WorkspaceMember", back_populates="workspace")


class WorkspaceCreate(BaseModel):
    name: str


class WorkspaceRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    owner_id: uuid.UUID
    role: str | None = None
