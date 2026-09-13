"""Dashboard aggregate endpoint."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database import get_db
from app.models import Disaster, DisasterStatus, DisasterZone, FieldTeam, Mission, Resource, TeamStatus, User
from app.utils.deps import get_current_user

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary")
def dashboard_summary(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    settings = get_settings()
    disasters = db.query(Disaster).all()
    zones = db.query(DisasterZone).all()
    resources = db.query(Resource).all()
    teams = db.query(FieldTeam).all()
    missions = db.query(Mission).order_by(Mission.created_at.desc()).limit(10).all()

    active = [d for d in disasters if d.status == DisasterStatus.ACTIVE]
    available_resources = sum(r.quantity_available for r in resources)
    predicted_demand = sum(z.food_demand + z.water_demand_litres + z.medical_kit_demand + z.shelter_demand for z in zones)
    shortage = max(0, predicted_demand - available_resources)
    active_teams = [t for t in teams if t.status != TeamStatus.AVAILABLE]

    critical_zones = sorted(
        zones,
        key=lambda z: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(
                z.priority.value if hasattr(z.priority, "value") else str(z.priority), 9
            ),
            -z.vulnerability_score,
        ),
    )[:8]

    return {
        "demo_mode": settings.demo_mode,
        "external_apis": settings.external_apis_configured,
        "cards": {
            "active_disasters": len(active),
            "affected_population": sum(d.affected_population for d in disasters),
            "available_resources": round(available_resources, 2),
            "predicted_demand": round(predicted_demand, 2),
            "resource_shortage": round(shortage, 2),
            "field_teams_active": len(active_teams),
        },
        "disasters": [
            {
                "id": d.id,
                "title": d.title,
                "latitude": d.latitude,
                "longitude": d.longitude,
                "severity": d.severity.value if hasattr(d.severity, "value") else d.severity,
                "status": d.status.value if hasattr(d.status, "value") else d.status,
                "affected_population": d.affected_population,
            }
            for d in disasters
        ],
        "zones": [
            {
                "id": z.id,
                "disaster_id": z.disaster_id,
                "name": z.name,
                "latitude": z.latitude,
                "longitude": z.longitude,
                "population": z.population,
                "severity": z.severity.value if hasattr(z.severity, "value") else z.severity,
                "priority": z.priority.value if hasattr(z.priority, "value") else z.priority,
                "building_damage_pct": z.building_damage_pct,
                "food_demand": z.food_demand,
                "water_demand_litres": z.water_demand_litres,
                "medical_kit_demand": z.medical_kit_demand,
                "shelter_demand": z.shelter_demand,
                "vulnerability_score": z.vulnerability_score,
            }
            for z in zones
        ],
        "critical_zones": [
            {
                "id": z.id,
                "name": z.name,
                "priority": z.priority.value if hasattr(z.priority, "value") else z.priority,
                "population": z.population,
                "food_demand": z.food_demand,
                "water_demand_litres": z.water_demand_litres,
            }
            for z in critical_zones
        ],
        "resources": [
            {
                "id": r.id,
                "name": r.name,
                "resource_type": r.resource_type,
                "quantity_available": r.quantity_available,
                "quantity_reserved": r.quantity_reserved,
                "quantity_deployed": r.quantity_deployed,
            }
            for r in resources
        ],
        "recent_missions": [
            {
                "id": m.id,
                "title": m.title,
                "status": m.status.value if hasattr(m.status, "value") else m.status,
                "priority": m.priority.value if hasattr(m.priority, "value") else m.priority,
                "disaster_id": m.disaster_id,
            }
            for m in missions
        ],
        "depots": [],
        "teams": [
            {
                "id": t.id,
                "name": t.name,
                "latitude": t.latitude,
                "longitude": t.longitude,
                "status": t.status.value if hasattr(t.status, "value") else t.status,
            }
            for t in teams
        ],
    }
