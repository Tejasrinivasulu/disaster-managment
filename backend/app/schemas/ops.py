"""Optimization and logistics route schemas/routes."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class AllocateRequest(BaseModel):
    disaster_id: int
    transport_capacity: Optional[float] = None
    supply_overrides: Optional[Dict[str, float]] = None


class RouteRequest(BaseModel):
    depot_id: int
    zone_id: int
    vehicle_type: str = "truck"
    resources: Optional[Dict[str, float]] = None


class ScenarioCreate(BaseModel):
    disaster_id: int
    name: str
    response_speed: str = Field(default="normal", pattern="^(fast|normal|limited)$")
    available_food: float = 0
    available_water: float = 0
    available_medical: float = 0
    available_shelter: float = 0
    transport_capacity: float = 0


class TeamCreate(BaseModel):
    name: str
    leader_name: str
    members_count: int = 5
    skills: Optional[str] = None
    latitude: float = 0
    longitude: float = 0


class TeamUpdate(BaseModel):
    name: Optional[str] = None
    leader_name: Optional[str] = None
    members_count: Optional[int] = None
    skills: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    status: Optional[str] = None
    assigned_disaster_id: Optional[int] = None


class MissionCreate(BaseModel):
    title: str
    instructions: Optional[str] = None
    disaster_id: int
    zone_id: int
    team_id: int
    resources_json: Optional[Dict[str, Any]] = None
    priority: str = "medium"
    deadline: Optional[str] = None


class MissionStatusUpdate(BaseModel):
    status: str
