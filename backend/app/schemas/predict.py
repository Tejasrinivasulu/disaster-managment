"""Demand prediction schemas compatible with resource_demand_ml_ready features."""

from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field


class DemandInput(BaseModel):
    """Core fields required by the API; extra dataset features are accepted."""

    model_config = ConfigDict(extra="allow")

    latitude: float
    longitude: float
    population: float = Field(gt=0)
    population_density: float = Field(ge=0)
    vulnerability_score: float = Field(ge=0, le=1)
    severity_score: float = Field(ge=0, le=1)
    building_damage_pct: float = Field(ge=0, le=100)
    road_damage_pct: float = Field(ge=0, le=100)
    rainfall: float = Field(ge=0)
    humidity: float = Field(ge=0, le=100)
    # Dataset uses percent values like 22.37; also accepts 0-1 fractions
    elderly_pct: float = Field(default=12.0, ge=0)
    children_pct: float = Field(default=22.0, ge=0)
    medical_dependency_pct: float = Field(default=8.0, ge=0)
    medically_dependent_pct: Optional[float] = None
    accessibility_score: float = Field(default=0.7, ge=0, le=1)
    disaster_type: str = "Flood"
    subtype: str = "River Flood"
    disaster_subtype: Optional[str] = None
    disaster_id: Optional[int] = None
    zone_id: Optional[int] = None


class DemandUpdateInput(DemandInput):
    reason: str = Field(min_length=3, description="Reason for recalculation")
    previous_food_demand: Optional[float] = None
    previous_water_demand_litres: Optional[float] = None
    previous_medical_kit_demand: Optional[float] = None
    previous_shelter_demand: Optional[float] = None


class DemandOutput(BaseModel):
    food_demand: float
    water_demand_litres: float
    medical_kit_demand: float
    shelter_demand: float
    confidence: Dict[str, str]
    models_used: Dict[str, str]
    base_demand: Dict[str, float]
    vulnerability_adjustment: float
    vulnerability_breakdown: Dict[str, float]
    formula: str
    dataset_rows: Optional[int] = None


class DemandUpdateOutput(DemandOutput):
    previous_demand: Dict[str, float]
    percentage_change: Dict[str, float]
    reason: str
