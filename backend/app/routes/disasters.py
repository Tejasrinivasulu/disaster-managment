"""Disaster and zone management routes."""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.database import get_db
from app.models import (
    Disaster,
    DisasterZone,
    PriorityOverride,
    User,
    UserRole,
)
from app.schemas.disaster import (
    DisasterCreate,
    DisasterOut,
    DisasterUpdate,
    PriorityOverrideCreate,
    PriorityOverrideOut,
    ZoneCreate,
    ZoneOut,
    ZoneUpdate,
)
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/disasters", tags=["Disasters"])

Coordinator = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN))


@router.get("", response_model=List[DisasterOut])
def list_disasters(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return (
        db.query(Disaster)
        .options(joinedload(Disaster.zones))
        .order_by(Disaster.created_at.desc())
        .all()
    )


@router.get("/{disaster_id}", response_model=DisasterOut)
def get_disaster(
    disaster_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    disaster = (
        db.query(Disaster)
        .options(joinedload(Disaster.zones))
        .filter(Disaster.id == disaster_id)
        .first()
    )
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")
    return disaster


@router.post("", response_model=DisasterOut, status_code=status.HTTP_201_CREATED)
def create_disaster(
    payload: DisasterCreate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    data = payload.model_dump(exclude={"zones"})
    disaster = Disaster(**data)
    db.add(disaster)
    db.flush()
    for z in payload.zones:
        db.add(DisasterZone(disaster_id=disaster.id, **z.model_dump()))
    db.commit()
    db.refresh(disaster)
    logger.info("Disaster %s created by user %s", disaster.id, user.id)
    return (
        db.query(Disaster)
        .options(joinedload(Disaster.zones))
        .filter(Disaster.id == disaster.id)
        .first()
    )


@router.patch("/{disaster_id}", response_model=DisasterOut)
def update_disaster(
    disaster_id: int,
    payload: DisasterUpdate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    disaster = db.get(Disaster, disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(disaster, key, value)
    db.commit()
    logger.info("Disaster %s updated by user %s", disaster_id, user.id)
    return (
        db.query(Disaster)
        .options(joinedload(Disaster.zones))
        .filter(Disaster.id == disaster_id)
        .first()
    )


@router.delete("/{disaster_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_disaster(
    disaster_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.ADMIN)),
):
    disaster = db.get(Disaster, disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")
    db.delete(disaster)
    db.commit()
    logger.info("Disaster %s deleted by admin %s", disaster_id, user.id)


zones_router = APIRouter(prefix="/zones", tags=["Zones"])


@zones_router.get("", response_model=List[ZoneOut])
def list_zones(
    disaster_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    q = db.query(DisasterZone)
    if disaster_id is not None:
        q = q.filter(DisasterZone.disaster_id == disaster_id)
    return q.order_by(DisasterZone.id).all()


@zones_router.post("/{disaster_id}", response_model=ZoneOut, status_code=201)
def add_zone(
    disaster_id: int,
    payload: ZoneCreate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    if not db.get(Disaster, disaster_id):
        raise HTTPException(status_code=404, detail="Disaster not found")
    zone = DisasterZone(disaster_id=disaster_id, **payload.model_dump())
    db.add(zone)
    db.commit()
    db.refresh(zone)
    logger.info("Zone %s added to disaster %s by %s", zone.id, disaster_id, user.id)
    return zone


@zones_router.patch("/{zone_id}", response_model=ZoneOut)
def update_zone(
    zone_id: int,
    payload: ZoneUpdate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    zone = db.get(DisasterZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(zone, key, value)
    db.commit()
    db.refresh(zone)
    return zone


@zones_router.post("/{zone_id}/priority-override", response_model=PriorityOverrideOut)
def override_priority(
    zone_id: int,
    payload: PriorityOverrideCreate,
    db: Session = Depends(get_db),
    user: User = Coordinator,
):
    zone = db.get(DisasterZone, zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")
    previous = zone.priority
    record = PriorityOverride(
        zone_id=zone.id,
        previous_priority=previous,
        new_priority=payload.new_priority,
        reason=payload.reason,
        changed_by=user.id,
    )
    zone.priority = payload.new_priority
    zone.priority_override = True
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info(
        "Priority override zone=%s %s→%s by user=%s",
        zone_id,
        previous,
        payload.new_priority,
        user.id,
    )
    return record
