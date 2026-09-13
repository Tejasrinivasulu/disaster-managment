"""Schemas for resources and depots."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field

from app.models import ResourceStatus


class DepotCreate(BaseModel):
    name: str
    location_name: str
    latitude: float
    longitude: float
    capacity: int = 10000
    is_active: bool = True


class DepotOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    location_name: str
    latitude: float
    longitude: float
    capacity: int
    is_active: bool


class ResourceCreate(BaseModel):
    depot_id: int
    resource_type: str
    name: str
    quantity_available: float = Field(ge=0)
    quantity_reserved: float = Field(default=0, ge=0)
    quantity_deployed: float = Field(default=0, ge=0)
    unit: str = "units"
    status: ResourceStatus = ResourceStatus.AVAILABLE


class ResourceUpdate(BaseModel):
    name: Optional[str] = None
    quantity_available: Optional[float] = None
    quantity_reserved: Optional[float] = None
    quantity_deployed: Optional[float] = None
    unit: Optional[str] = None
    status: Optional[ResourceStatus] = None
    depot_id: Optional[int] = None


class ResourceAssign(BaseModel):
    quantity: float = Field(gt=0)
    action: str = Field(description="reserve | deploy | release")


class ResourceOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    depot_id: int
    resource_type: str
    name: str
    quantity_available: float
    quantity_reserved: float
    quantity_deployed: float
    unit: str
    status: ResourceStatus
    updated_at: datetime


class DepotWithResources(DepotOut):
    resources: List[ResourceOut] = []
