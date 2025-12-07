import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel, ConfigDict
from api.db.base import Base
from api.db.types import UUID


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"

    id = Column(UUID, primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID, ForeignKey("workspaces.id"))
    user_id = Column(UUID, ForeignKey("users.id"))
    role = Column(String, default="member")

    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User")


class WorkspaceMemberCreate(BaseModel):
    email: str


class WorkspaceMemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    user_id: uuid.UUID
    role: str
    email: str | None = None
