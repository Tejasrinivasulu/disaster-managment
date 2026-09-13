"""Resource allocation optimization routes."""

import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Disaster,
    DisasterZone,
    PriorityLevel,
    Resource,
    ResourceAllocation,
    User,
    UserRole,
)
from app.optimization.allocator import allocate_resources
from app.schemas.ops import AllocateRequest
from app.utils.deps import require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/optimization", tags=["Optimization"])


@router.post("/allocate")
def optimize_allocation(
    payload: AllocateRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    disaster = db.get(Disaster, payload.disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")

    zones = db.query(DisasterZone).filter(DisasterZone.disaster_id == payload.disaster_id).all()
    if not zones:
        raise HTTPException(status_code=400, detail="No zones for this disaster")

    # Ensure demands exist; if zero, use a simple heuristic fallback
    zone_payload = []
    for z in zones:
        food = z.food_demand or z.population * 0.3
        water = z.water_demand_litres or z.population * 15
        medical = z.medical_kit_demand or z.population * 0.03
        shelter = z.shelter_demand or z.population * 0.12
        zone_payload.append(
            {
                "id": z.id,
                "name": z.name,
                "priority": z.priority.value if isinstance(z.priority, PriorityLevel) else z.priority,
                "accessibility_score": z.accessibility_score,
                "food_demand": food,
                "water_demand_litres": water,
                "medical_kit_demand": medical,
                "shelter_demand": shelter,
            }
        )

    if payload.supply_overrides:
        supplies = payload.supply_overrides
    else:
        resources = db.query(Resource).all()
        supplies = {
            "food_packets": 0.0,
            "water": 0.0,
            "medical_kits": 0.0,
            "shelter": 0.0,
        }
        for r in resources:
            if r.resource_type in supplies:
                supplies[r.resource_type] += float(r.quantity_available)

    try:
        result = allocate_resources(zone_payload, supplies, payload.transport_capacity)
    except Exception as exc:
        logger.exception("Allocation failed")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    # Persist allocations
    for row in result["allocations"]:
        # Find a matching resource row if possible
        resource = (
            db.query(Resource)
            .filter(Resource.resource_type == row["resource"])
            .order_by(Resource.quantity_available.desc())
            .first()
        )
        if not resource:
            continue
        db.add(
            ResourceAllocation(
                zone_id=row["zone_id"],
                resource_id=resource.id,
                resource_type=row["resource"],
                requested_quantity=row["requested_quantity"],
                allocated_quantity=row["allocated_quantity"],
                shortage=row["shortage"],
                coverage_pct=row["coverage_percentage"],
                priority=PriorityLevel(row["priority"])
                if row["priority"] in PriorityLevel._value2member_map_
                else PriorityLevel.MEDIUM,
            )
        )
    db.commit()
    logger.info("Allocation completed for disaster %s by user %s", payload.disaster_id, user.id)
    return result
