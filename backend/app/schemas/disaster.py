"""Schemas for disasters and zones."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import DisasterStatus, PriorityLevel


class ZoneCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    latitude: float
    longitude: float
    population: int = 0
    population_density: float = 0
    vulnerability_score: float = Field(default=0.5, ge=0, le=1)
    accessibility_score: float = Field(default=0.7, ge=0, le=1)
    building_damage_pct: float = Field(default=0, ge=0, le=100)
    road_damage_pct: float = Field(default=0, ge=0, le=100)
    rainfall: float = 0
    humidity: float = 50
    severity: PriorityLevel = PriorityLevel.MEDIUM
    priority: PriorityLevel = PriorityLevel.MEDIUM


class ZoneUpdate(BaseModel):
    name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    population: Optional[int] = None
    population_density: Optional[float] = None
    vulnerability_score: Optional[float] = None
    accessibility_score: Optional[float] = None
    building_damage_pct: Optional[float] = None
    road_damage_pct: Optional[float] = None
    rainfall: Optional[float] = None
    humidity: Optional[float] = None
    severity: Optional[PriorityLevel] = None
    priority: Optional[PriorityLevel] = None


class ZoneOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disaster_id: int
    name: str
    latitude: float
    longitude: float
    population: int
    population_density: float
    vulnerability_score: float
    accessibility_score: float
    building_damage_pct: float
    road_damage_pct: float
    rainfall: float
    humidity: float
    severity: PriorityLevel
    priority: PriorityLevel
    priority_override: bool
    food_demand: float
    water_demand_litres: float
    medical_kit_demand: float
    shelter_demand: float


class DisasterCreate(BaseModel):
    disaster_type: str
    subtype: Optional[str] = None
    title: str
    description: Optional[str] = None
    location_name: str
    latitude: float
    longitude: float
    severity: PriorityLevel = PriorityLevel.MEDIUM
    status: DisasterStatus = DisasterStatus.ACTIVE
    affected_population: int = 0
    zones: List[ZoneCreate] = []


class DisasterUpdate(BaseModel):
    disaster_type: Optional[str] = None
    subtype: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    location_name: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    severity: Optional[PriorityLevel] = None
    status: Optional[DisasterStatus] = None
    affected_population: Optional[int] = None


class DisasterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    disaster_type: str
    subtype: Optional[str]
    title: str
    description: Optional[str]
    event_date: datetime
    location_name: str
    latitude: float
    longitude: float
    severity: PriorityLevel
    status: DisasterStatus
    affected_population: int
    created_at: datetime
    updated_at: datetime
    zones: List[ZoneOut] = []


class PriorityOverrideCreate(BaseModel):
    new_priority: PriorityLevel
    reason: str = Field(min_length=3)


class PriorityOverrideOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    previous_priority: PriorityLevel
    new_priority: PriorityLevel
    reason: str
    changed_by: Optional[int]
    created_at: datetime
