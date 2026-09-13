"""Field teams and missions routes."""

import logging
from datetime import datetime
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Disaster,
    DisasterZone,
    FieldTeam,
    Mission,
    MissionStatus,
    PriorityLevel,
    TeamStatus,
    User,
    UserRole,
)
from app.schemas.ops import MissionCreate, MissionStatusUpdate, TeamCreate, TeamUpdate
from app.utils.deps import get_current_user, require_roles
from pydantic import BaseModel, ConfigDict

logger = logging.getLogger(__name__)
teams_router = APIRouter(prefix="/teams", tags=["Field Teams"])
missions_router = APIRouter(prefix="/missions", tags=["Missions"])


class TeamOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    leader_name: str
    members_count: int
    skills: str | None
    latitude: float
    longitude: float
    status: TeamStatus
    assigned_disaster_id: int | None


class MissionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    title: str
    instructions: str | None
    disaster_id: int
    zone_id: int
    team_id: int
    assigned_by: int | None
    resources_json: dict | None
    priority: PriorityLevel
    status: MissionStatus
    deadline: datetime | None
    created_at: datetime


@teams_router.get("", response_model=List[TeamOut])
def list_teams(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return db.query(FieldTeam).order_by(FieldTeam.id).all()


@teams_router.post("", response_model=TeamOut, status_code=201)
def create_team(
    payload: TeamCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    team = FieldTeam(**payload.model_dump())
    db.add(team)
    db.commit()
    db.refresh(team)
    logger.info("Team %s created by %s", team.id, user.id)
    return team


@teams_router.patch("/{team_id}", response_model=TeamOut)
def update_team(
    team_id: int,
    payload: TeamUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN, UserRole.FIELD_TEAM)),
):
    team = db.get(FieldTeam, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    data = payload.model_dump(exclude_unset=True)
    if "status" in data and data["status"]:
        data["status"] = TeamStatus(data["status"])
    for k, v in data.items():
        setattr(team, k, v)
    db.commit()
    db.refresh(team)
    return team


@missions_router.get("", response_model=List[MissionOut])
def list_missions(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(Mission).order_by(Mission.created_at.desc())
    return q.all()


@missions_router.get("/{mission_id}/detail")
def mission_detail(
    mission_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    mission = db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    disaster = db.get(Disaster, mission.disaster_id)
    zone = db.get(DisasterZone, mission.zone_id)
    team = db.get(FieldTeam, mission.team_id)
    from app.models import ResourceDepot

    depot = db.query(ResourceDepot).order_by(ResourceDepot.id).first()
    route = None
    if depot and zone:
        from app.routes.routes import local_route

        route = local_route(
            depot.latitude,
            depot.longitude,
            zone.latitude,
            zone.longitude,
            zone.road_damage_pct,
            zone.accessibility_score,
        )
        route["depot"] = {
            "id": depot.id,
            "name": depot.name,
            "latitude": depot.latitude,
            "longitude": depot.longitude,
        }
    return {
        "mission": MissionOut.model_validate(mission).model_dump(),
        "disaster": {
            "id": disaster.id,
            "title": disaster.title,
            "type": disaster.disaster_type,
            "location": disaster.location_name,
            "severity": disaster.severity.value if disaster else None,
        }
        if disaster
        else None,
        "zone": {
            "id": zone.id,
            "name": zone.name,
            "latitude": zone.latitude,
            "longitude": zone.longitude,
            "population": zone.population,
            "building_damage_pct": zone.building_damage_pct,
            "road_damage_pct": zone.road_damage_pct,
            "priority": zone.priority.value,
            "vulnerability_score": zone.vulnerability_score,
        }
        if zone
        else None,
        "team": {
            "id": team.id,
            "name": team.name,
            "leader_name": team.leader_name,
            "status": team.status.value,
        }
        if team
        else None,
        "resource_manifest": mission.resources_json or {},
        "route": route,
        "alerts": [
            {
                "level": "critical" if (zone and zone.priority.value == "critical") else "info",
                "message": "High-priority zone — expedite delivery"
                if zone and zone.priority.value in ("critical", "high")
                else "Standard priority mission",
            }
        ],
    }

@missions_router.post("", response_model=MissionOut, status_code=201)
def create_mission(
    payload: MissionCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    if not db.get(Disaster, payload.disaster_id):
        raise HTTPException(status_code=404, detail="Disaster not found")
    if not db.get(DisasterZone, payload.zone_id):
        raise HTTPException(status_code=404, detail="Zone not found")
    team = db.get(FieldTeam, payload.team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    deadline = None
    if payload.deadline:
        deadline = datetime.fromisoformat(payload.deadline.replace("Z", "+00:00"))

    mission = Mission(
        title=payload.title,
        instructions=payload.instructions,
        disaster_id=payload.disaster_id,
        zone_id=payload.zone_id,
        team_id=payload.team_id,
        assigned_by=user.id,
        resources_json=payload.resources_json,
        priority=PriorityLevel(payload.priority),
        status=MissionStatus.ASSIGNED,
        deadline=deadline,
    )
    team.status = TeamStatus.ASSIGNED
    team.assigned_disaster_id = payload.disaster_id
    db.add(mission)
    db.commit()
    db.refresh(mission)
    logger.info("Mission %s assigned by %s", mission.id, user.id)
    return mission


@missions_router.patch("/{mission_id}/status", response_model=MissionOut)
def update_mission_status(
    mission_id: int,
    payload: MissionStatusUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.FIELD_TEAM, UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    mission = db.get(Mission, mission_id)
    if not mission:
        raise HTTPException(status_code=404, detail="Mission not found")
    try:
        mission.status = MissionStatus(payload.status)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="Invalid mission status") from exc

    team = db.get(FieldTeam, mission.team_id)
    if team:
        status_map = {
            MissionStatus.ASSIGNED: TeamStatus.ASSIGNED,
            MissionStatus.IN_PROGRESS: TeamStatus.ON_SITE,
            MissionStatus.COMPLETED: TeamStatus.COMPLETED,
            MissionStatus.CANCELLED: TeamStatus.AVAILABLE,
        }
        if mission.status == MissionStatus.IN_PROGRESS:
            team.status = TeamStatus.EN_ROUTE
        elif mission.status in status_map:
            team.status = status_map[mission.status]
        if mission.status == MissionStatus.COMPLETED:
            team.status = TeamStatus.AVAILABLE
            team.assigned_disaster_id = None

    db.commit()
    db.refresh(mission)
    logger.info("Mission %s status → %s by %s", mission_id, payload.status, user.id)
    return mission
