"""Logistics routing with local haversine fallback and optional OSRM provider."""

from __future__ import annotations

import logging
import math
from typing import Any, Dict, List, Tuple

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import DisasterZone, ResourceDepot, RoutePlan, User, UserRole
from app.schemas.ops import RouteRequest
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["Logistics"])


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def local_route(
    depot_lat: float,
    depot_lon: float,
    zone_lat: float,
    zone_lon: float,
    road_damage_pct: float = 0,
    accessibility_score: float = 1.0,
) -> Dict[str, Any]:
    distance = haversine_km(depot_lat, depot_lon, zone_lat, zone_lon)
    # Damage and accessibility inflate effective travel distance/time
    damage_factor = 1 + (road_damage_pct / 100.0) * 0.8
    access_factor = 1 + max(0.0, 1.0 - accessibility_score) * 0.6
    effective_km = distance * damage_factor * access_factor
    # Assume average speed 35 km/h under disaster conditions
    hours = effective_km / 35.0
    geometry = {
        "type": "LineString",
        "coordinates": [[depot_lon, depot_lat], [zone_lon, zone_lat]],
        "note": "Local straight-line approximation (not live road routing)",
    }
    return {
        "distance_km": round(effective_km, 2),
        "estimated_time_hours": round(hours, 2),
        "route_geometry": geometry,
        "provider": "local_haversine",
        "is_realtime": False,
        "demo_label": "Local distance estimate (not live traffic routing)",
    }


@router.post("/plan")
def plan_route(
    payload: RouteRequest,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    depot = db.get(ResourceDepot, payload.depot_id)
    zone = db.get(DisasterZone, payload.zone_id)
    if not depot or not zone:
        raise HTTPException(status_code=404, detail="Depot or zone not found")

    settings = get_settings()
    # Abstraction point for future OSRM/Google routing provider
    if settings.osrm_api_url:
        # Provider configured but not implemented for live calls in this build —
        # fall back explicitly and label as non-realtime.
        route = local_route(
            depot.latitude,
            depot.longitude,
            zone.latitude,
            zone.longitude,
            zone.road_damage_pct,
            zone.accessibility_score,
        )
        route["provider"] = "osrm_configured_fallback_local"
        route["demo_label"] = "OSRM URL set but live call not enabled; using local estimate"
    else:
        route = local_route(
            depot.latitude,
            depot.longitude,
            zone.latitude,
            zone.longitude,
            zone.road_damage_pct,
            zone.accessibility_score,
        )

    record = RoutePlan(
        depot_id=depot.id,
        zone_id=zone.id,
        distance_km=route["distance_km"],
        estimated_time_hours=route["estimated_time_hours"],
        vehicle_type=payload.vehicle_type,
        resources_json=payload.resources,
        route_geometry=route["route_geometry"],
        provider=route["provider"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    logger.info("Route planned %s→%s by user %s", depot.id, zone.id, user.id)
    return {
        "id": record.id,
        "depot": {"id": depot.id, "name": depot.name, "lat": depot.latitude, "lon": depot.longitude},
        "zone": {"id": zone.id, "name": zone.name, "lat": zone.latitude, "lon": zone.longitude},
        "vehicle_type": payload.vehicle_type,
        "resources_transported": payload.resources or {},
        **route,
    }


@router.get("")
def list_routes(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    rows = db.query(RoutePlan).order_by(RoutePlan.created_at.desc()).limit(100).all()
    return [
        {
            "id": r.id,
            "depot_id": r.depot_id,
            "zone_id": r.zone_id,
            "distance_km": r.distance_km,
            "estimated_time_hours": r.estimated_time_hours,
            "vehicle_type": r.vehicle_type,
            "resources_json": r.resources_json,
            "route_geometry": r.route_geometry,
            "provider": r.provider,
            "created_at": r.created_at,
        }
        for r in rows
    ]
