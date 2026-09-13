"""Admin user management and audit log routes."""

import logging
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, EmailStr, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AuditLog, User, UserRole
from app.schemas.auth import UserCreate, UserOut
from app.services.audit import write_audit
from app.utils.deps import get_current_user, require_roles
from app.utils.security import hash_password

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    password: Optional[str] = Field(default=None, min_length=6)


class AuditOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int | None
    action: str
    entity_type: str | None
    entity_id: int | None
    details: str | None
    created_at: object


@router.get("/users", response_model=List[UserOut])
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    return db.query(User).order_by(User.id).all()


@router.post("/users", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
):
    if db.query(User).filter(User.email == payload.email.lower()).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email.lower(),
        full_name=payload.full_name,
        hashed_password=hash_password(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    write_audit(
        db,
        user_id=admin.id,
        action="user.create",
        entity_type="user",
        entity_id=user.id,
        details=f"Created {user.email} as {user.role.value}",
    )
    return user


@router.patch("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(require_roles(UserRole.ADMIN)),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    data = payload.model_dump(exclude_unset=True)
    password = data.pop("password", None)
    for k, v in data.items():
        setattr(user, k, v)
    if password:
        user.hashed_password = hash_password(password)
    db.commit()
    db.refresh(user)
    write_audit(
        db,
        user_id=admin.id,
        action="user.update",
        entity_type="user",
        entity_id=user.id,
        details=str(payload.model_dump(exclude_unset=True)),
    )
    return user


@router.get("/audit-logs", response_model=List[AuditOut])
def list_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    return (
        db.query(AuditLog)
        .order_by(AuditLog.created_at.desc())
        .limit(min(limit, 500))
        .all()
    )


@router.get("/overview")
def admin_overview(
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(UserRole.ADMIN)),
):
    from app.models import Disaster, FieldTeam, Mission, Resource, ResourceDepot

    return {
        "users": db.query(User).count(),
        "active_users": db.query(User).filter(User.is_active.is_(True)).count(),
        "disasters": db.query(Disaster).count(),
        "depots": db.query(ResourceDepot).count(),
        "resources": db.query(Resource).count(),
        "teams": db.query(FieldTeam).count(),
        "missions": db.query(Mission).count(),
        "audit_events": db.query(AuditLog).count(),
    }
