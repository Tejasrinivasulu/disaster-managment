"""Resource allocation optimization routes."""

import logging
from collections import defaultdict
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

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


def _zone_ids_for_disaster(db: Session, disaster_id: int) -> list[int]:
    return [
        z.id
        for z in db.query(DisasterZone.id).filter(DisasterZone.disaster_id == disaster_id).all()
    ]


def _build_by_zone(allocations: list[dict]) -> list[dict]:
    by_zone: dict[int, dict] = {}
    for row in allocations:
        zid = row["zone_id"]
        entry = by_zone.setdefault(
            zid,
            {
                "zone_id": zid,
                "zone": row.get("zone", str(zid)),
                "priority": row.get("priority", "medium"),
                "resources": {},
                "lines": [],
            },
        )
        entry["resources"][row["resource"]] = round(float(row["allocated_quantity"]), 2)
        entry["lines"].append(row)
    return list(by_zone.values())


def _serialize_plan(allocations_rows, supplies=None, summary=None, solver_status=None):
    allocations = []
    for row in allocations_rows:
        zone_name = row.zone.name if getattr(row, "zone", None) else str(row.zone_id)
        priority = row.priority.value if hasattr(row.priority, "value") else row.priority
        allocations.append(
            {
                "zone_id": row.zone_id,
                "zone": zone_name,
                "resource": row.resource_type,
                "requested_quantity": row.requested_quantity,
                "allocated_quantity": row.allocated_quantity,
                "shortage": row.shortage,
                "coverage_percentage": row.coverage_pct,
                "priority": priority,
            }
        )
    if summary is None:
        total_req = sum(a["requested_quantity"] for a in allocations) or 1
        total_all = sum(a["allocated_quantity"] for a in allocations)
        summary = {
            "total_requested": round(total_req, 2),
            "total_allocated": round(total_all, 2),
            "overall_coverage_pct": round(total_all / total_req * 100, 2),
            "solver_status": solver_status or "stored",
        }
    return {
        "allocations": allocations,
        "by_zone": _build_by_zone(allocations),
        "summary": summary,
        "supplies_used": supplies or {},
        "pipeline": {
            "next_logistics": "/logistics",
            "next_mission": "/missions",
            "note": "Use by_zone[].resources when planning routes or assigning missions.",
        },
    }


@router.get("/plan/{disaster_id}")
def get_allocation_plan(
    disaster_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN, UserRole.FIELD_TEAM)
    ),
):
    """Return the current (latest) allocation plan for a disaster."""
    disaster = db.get(Disaster, disaster_id)
    if not disaster:
        raise HTTPException(status_code=404, detail="Disaster not found")

    zone_ids = _zone_ids_for_disaster(db, disaster_id)
    if not zone_ids:
        return {
            "disaster_id": disaster_id,
            "allocations": [],
            "by_zone": [],
            "summary": None,
            "message": "No zones for this disaster",
        }

    rows = (
        db.query(ResourceAllocation)
        .options(joinedload(ResourceAllocation.zone))
        .filter(ResourceAllocation.zone_id.in_(zone_ids))
        .order_by(ResourceAllocation.created_at.desc())
        .all()
    )
    if not rows:
        return {
            "disaster_id": disaster_id,
            "allocations": [],
            "by_zone": [],
            "summary": None,
            "message": "No allocation plan yet — run Resource Allocation first",
        }

    latest_ts = rows[0].created_at
    batch = [r for r in rows if r.created_at == latest_ts]
    plan = _serialize_plan(batch)
    plan["disaster_id"] = disaster_id
    plan["created_at"] = latest_ts.isoformat() if latest_ts else None
    return plan


@router.get("/plan/{disaster_id}/zone/{zone_id}")
def get_zone_allocation(
    disaster_id: int,
    zone_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(
        require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN, UserRole.FIELD_TEAM)
    ),
):
    """Resources allocated to one zone (for logistics / mission manifests)."""
    plan = get_allocation_plan(disaster_id, db, user)
    match = next((z for z in plan.get("by_zone", []) if z["zone_id"] == zone_id), None)
    if not match:
        return {
            "disaster_id": disaster_id,
            "zone_id": zone_id,
            "resources": {},
            "message": "No allocation for this zone yet",
        }
    return {
        "disaster_id": disaster_id,
        "zone_id": zone_id,
        "zone": match["zone"],
        "priority": match["priority"],
        "resources": match["resources"],
        "lines": match.get("lines", []),
    }


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

    zone_ids = [z.id for z in zones]
    previous = (
        db.query(ResourceAllocation)
        .filter(ResourceAllocation.zone_id.in_(zone_ids))
        .all()
    )
    for old in previous:
        res = db.get(Resource, old.resource_id)
        if res and old.allocated_quantity:
            release = min(float(old.allocated_quantity), float(res.quantity_reserved))
            res.quantity_reserved = max(0.0, float(res.quantity_reserved) - release)
            res.quantity_available = float(res.quantity_available) + release
        db.delete(old)
    db.flush()

    now = datetime.now(timezone.utc)
    reserved_total = defaultdict(float)

    for row in result["allocations"]:
        resource = (
            db.query(Resource)
            .filter(Resource.resource_type == row["resource"])
            .order_by(Resource.quantity_available.desc())
            .first()
        )
        if not resource:
            continue

        take = min(float(row["allocated_quantity"]), float(resource.quantity_available))
        resource.quantity_available = float(resource.quantity_available) - take
        resource.quantity_reserved = float(resource.quantity_reserved) + take
        reserved_total[row["resource"]] += take

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
                created_at=now,
            )
        )

    db.commit()
    logger.info("Allocation completed for disaster %s by user %s", payload.disaster_id, user.id)

    return {
        "disaster_id": payload.disaster_id,
        "allocations": result["allocations"],
        "by_zone": _build_by_zone(result["allocations"]),
        "summary": result["summary"],
        "supplies_available": supplies,
        "reserved_from_stock": dict(reserved_total),
        "created_at": now.isoformat(),
        "pipeline": {
            "next_logistics": "/logistics",
            "next_mission": "/missions",
            "note": "Use by_zone[].resources when planning routes or assigning missions.",
        },
        "message": (
            "Allocation plan saved. Stock moved available → reserved. "
            "Next: plan logistics routes, then assign missions using these quantities."
        ),
    }
