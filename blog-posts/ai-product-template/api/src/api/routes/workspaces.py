import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from api.db.session import get_db
from api.auth import get_current_user
from api.models.user import User
from api.models.workspace import Workspace, WorkspaceCreate, WorkspaceRead
from api.models.workspace_member import (
    WorkspaceMember,
    WorkspaceMemberCreate,
    WorkspaceMemberRead,
)

router = APIRouter()


def get_user_role(
    db: Session, workspace_id: uuid.UUID, user_id: uuid.UUID
) -> str | None:
    if (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.owner_id == user_id)
        .first()
    ):
        return "owner"
    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
        .first()
    )
    return member.role if member else None


@router.post("/", response_model=WorkspaceRead)
def create_workspace(
    workspace: WorkspaceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    db_workspace = Workspace(name=workspace.name, owner_id=current_user.id)
    db.add(db_workspace)
    db.commit()
    db.refresh(db_workspace)
    return WorkspaceRead(
        id=db_workspace.id,
        name=db_workspace.name,
        owner_id=db_workspace.owner_id,
        role="owner",
    )


@router.get("/", response_model=list[WorkspaceRead])
def list_workspaces(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    owned = db.query(Workspace).filter(Workspace.owner_id == current_user.id).all()
    member_of = (
        db.query(Workspace)
        .join(WorkspaceMember)
        .filter(WorkspaceMember.user_id == current_user.id)
        .all()
    )

    results = []
    for w in owned:
        results.append(
            WorkspaceRead(id=w.id, name=w.name, owner_id=w.owner_id, role="owner")
        )
    for w in member_of:
        if w.id not in [r.id for r in results]:
            member = (
                db.query(WorkspaceMember)
                .filter(
                    WorkspaceMember.workspace_id == w.id,
                    WorkspaceMember.user_id == current_user.id,
                )
                .first()
            )
            results.append(
                WorkspaceRead(
                    id=w.id,
                    name=w.name,
                    owner_id=w.owner_id,
                    role=member.role if member else "member",
                )
            )
    return results


@router.get("/{workspace_id}", response_model=WorkspaceRead)
def get_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = get_user_role(db, workspace_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied")
    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found")
    return WorkspaceRead(
        id=workspace.id, name=workspace.name, owner_id=workspace.owner_id, role=role
    )


@router.delete("/{workspace_id}")
def delete_workspace(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.owner_id == current_user.id)
        .first()
    )
    if not workspace:
        raise HTTPException(status_code=403, detail="Only owner can delete workspace")
    db.query(WorkspaceMember).filter(
        WorkspaceMember.workspace_id == workspace_id
    ).delete()
    db.delete(workspace)
    db.commit()
    return {"ok": True}


@router.get("/{workspace_id}/members", response_model=list[WorkspaceMemberRead])
def list_members(
    workspace_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    role = get_user_role(db, workspace_id, current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Access denied")

    workspace = db.query(Workspace).filter(Workspace.id == workspace_id).first()
    owner = db.query(User).filter(User.id == workspace.owner_id).first()

    results = [
        WorkspaceMemberRead(
            id=owner.id, user_id=owner.id, role="owner", email=owner.email
        )
    ]
    members = (
        db.query(WorkspaceMember)
        .filter(WorkspaceMember.workspace_id == workspace_id)
        .all()
    )
    for m in members:
        user = db.query(User).filter(User.id == m.user_id).first()
        results.append(
            WorkspaceMemberRead(
                id=m.id,
                user_id=m.user_id,
                role=m.role,
                email=user.email if user else None,
            )
        )
    return results


@router.post("/{workspace_id}/members", response_model=WorkspaceMemberRead)
def add_member(
    workspace_id: uuid.UUID,
    member: WorkspaceMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.owner_id == current_user.id)
        .first()
    )
    if not workspace:
        raise HTTPException(status_code=403, detail="Only owner can add members")

    user = db.query(User).filter(User.email == member.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    existing = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user.id,
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="User already a member")

    db_member = WorkspaceMember(
        workspace_id=workspace_id, user_id=user.id, role="member"
    )
    db.add(db_member)
    db.commit()
    db.refresh(db_member)
    return WorkspaceMemberRead(
        id=db_member.id,
        user_id=db_member.user_id,
        role=db_member.role,
        email=user.email,
    )


@router.delete("/{workspace_id}/members/{member_id}")
def remove_member(
    workspace_id: uuid.UUID,
    member_id: uuid.UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    workspace = (
        db.query(Workspace)
        .filter(Workspace.id == workspace_id, Workspace.owner_id == current_user.id)
        .first()
    )
    if not workspace:
        raise HTTPException(status_code=403, detail="Only owner can remove members")

    member = (
        db.query(WorkspaceMember)
        .filter(
            WorkspaceMember.id == member_id,
            WorkspaceMember.workspace_id == workspace_id,
        )
        .first()
    )
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    db.delete(member)
    db.commit()
    return {"ok": True}
