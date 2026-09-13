"""Resource inventory and depot routes."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import Resource, ResourceDepot, ResourceStatus, User, UserRole
from app.schemas.resource import (
    DepotCreate,
    DepotOut,
    DepotWithResources,
    ResourceAssign,
    ResourceCreate,
    ResourceOut,
    ResourceUpdate,
)
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/resources", tags=["Resources"])
Coordinator = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN))


@router.get("/depots", response_model=List[DepotWithResources])
def list_depots(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return db.query(ResourceDepot).options(joinedload(ResourceDepot.resources)).all()


@router.post("/depots", response_model=DepotOut, status_code=201)
def create_depot(
    payload: DepotCreate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    depot = ResourceDepot(**payload.model_dump())
    db.add(depot)
    db.commit()
    db.refresh(depot)
    logger.info("Depot %s created by %s", depot.id, user.id)
    return depot


@router.get("", response_model=List[ResourceOut])
def list_resources(
    depot_id: int | None = None,
    resource_type: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(Resource)
    if depot_id is not None:
        q = q.filter(Resource.depot_id == depot_id)
    if resource_type:
        q = q.filter(Resource.resource_type == resource_type)
    return q.order_by(Resource.id).all()


@router.post("", response_model=ResourceOut, status_code=status.HTTP_201_CREATED)
def create_resource(
    payload: ResourceCreate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    if not db.get(ResourceDepot, payload.depot_id):
        raise HTTPException(status_code=404, detail="Depot not found")
    resource = Resource(**payload.model_dump())
    db.add(resource)
    db.commit()
    db.refresh(resource)
    logger.info("Resource %s created by %s", resource.id, user.id)
    return resource


@router.patch("/{resource_id}", response_model=ResourceOut)
def update_resource(
    resource_id: int,
    payload: ResourceUpdate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(resource, key, value)
    db.commit()
    db.refresh(resource)
    return resource


@router.post("/{resource_id}/assign", response_model=ResourceOut)
def assign_resource(
    resource_id: int,
    payload: ResourceAssign,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")

    qty = payload.quantity
    action = payload.action.lower()
    if action == "reserve":
        if resource.quantity_available < qty:
            raise HTTPException(status_code=400, detail="Insufficient available quantity")
        resource.quantity_available -= qty
        resource.quantity_reserved += qty
    elif action == "deploy":
        if resource.quantity_reserved >= qty:
            resource.quantity_reserved -= qty
            resource.quantity_deployed += qty
        elif resource.quantity_available >= qty:
            resource.quantity_available -= qty
            resource.quantity_deployed += qty
        else:
            raise HTTPException(status_code=400, detail="Insufficient quantity to deploy")
    elif action == "release":
        if resource.quantity_reserved < qty:
            raise HTTPException(status_code=400, detail="Insufficient reserved quantity")
        resource.quantity_reserved -= qty
        resource.quantity_available += qty
    else:
        raise HTTPException(status_code=400, detail="action must be reserve, deploy, or release")

    total = resource.quantity_available + resource.quantity_reserved + resource.quantity_deployed
    if resource.quantity_available <= 0 and resource.quantity_reserved <= 0:
        resource.status = ResourceStatus.DEPLETED if resource.quantity_deployed > 0 else ResourceStatus.DEPLETED
    elif resource.quantity_deployed > 0:
        resource.status = ResourceStatus.DEPLOYED
    elif resource.quantity_reserved > 0:
        resource.status = ResourceStatus.RESERVED
    else:
        resource.status = ResourceStatus.AVAILABLE

    db.commit()
    db.refresh(resource)
    logger.info("Resource %s %s qty=%s by user=%s total_track=%s", resource_id, action, qty, user.id, total)
    return resource


@router.delete("/{resource_id}", status_code=204)
def delete_resource(
    resource_id: int,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    resource = db.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    db.delete(resource)
    db.commit()
    logger.info("Resource %s deleted by %s", resource_id, user.id)
