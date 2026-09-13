"""SQLAlchemy ORM models for the disaster response system."""

from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    JSON,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class UserRole(str, PyEnum):
    ADMIN = "admin"
    RELIEF_COORDINATOR = "relief_coordinator"
    FIELD_TEAM = "field_team"


class DisasterStatus(str, PyEnum):
    ACTIVE = "active"
    MONITORING = "monitoring"
    RECOVERY = "recovery"
    CLOSED = "closed"


class PriorityLevel(str, PyEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResourceStatus(str, PyEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    DEPLOYED = "deployed"
    DEPLETED = "depleted"


class TeamStatus(str, PyEnum):
    AVAILABLE = "available"
    ASSIGNED = "assigned"
    EN_ROUTE = "en_route"
    ON_SITE = "on_site"
    COMPLETED = "completed"


class MissionStatus(str, PyEnum):
    PLANNED = "planned"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.FIELD_TEAM, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    missions_led = relationship("Mission", back_populates="assigned_by_user", foreign_keys="Mission.assigned_by")
    field_reports = relationship("FieldReport", back_populates="reporter")
    priority_overrides = relationship("PriorityOverride", back_populates="changed_by_user")
    audit_logs = relationship("AuditLog", back_populates="user")


class Disaster(Base):
    __tablename__ = "disasters"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_type: Mapped[str] = mapped_column(String(100), nullable=False)
    subtype: Mapped[str | None] = mapped_column(String(100))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    event_date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    severity: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status: Mapped[DisasterStatus] = mapped_column(Enum(DisasterStatus), default=DisasterStatus.ACTIVE)
    affected_population: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    zones = relationship("DisasterZone", back_populates="disaster", cascade="all, delete-orphan")
    missions = relationship("Mission", back_populates="disaster")
    predictions = relationship("DemandPrediction", back_populates="disaster")
    scenarios = relationship("Scenario", back_populates="disaster")


class DisasterZone(Base):
    __tablename__ = "disaster_zones"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_id: Mapped[int] = mapped_column(ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    population: Mapped[int] = mapped_column(Integer, default=0)
    population_density: Mapped[float] = mapped_column(Float, default=0.0)
    vulnerability_score: Mapped[float] = mapped_column(Float, default=0.5)
    accessibility_score: Mapped[float] = mapped_column(Float, default=0.7)
    building_damage_pct: Mapped[float] = mapped_column(Float, default=0.0)
    road_damage_pct: Mapped[float] = mapped_column(Float, default=0.0)
    rainfall: Mapped[float] = mapped_column(Float, default=0.0)
    humidity: Mapped[float] = mapped_column(Float, default=50.0)
    severity: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    priority_override: Mapped[bool] = mapped_column(Boolean, default=False)
    food_demand: Mapped[float] = mapped_column(Float, default=0.0)
    water_demand_litres: Mapped[float] = mapped_column(Float, default=0.0)
    medical_kit_demand: Mapped[float] = mapped_column(Float, default=0.0)
    shelter_demand: Mapped[float] = mapped_column(Float, default=0.0)

    disaster = relationship("Disaster", back_populates="zones")
    allocations = relationship("ResourceAllocation", back_populates="zone")
    missions = relationship("Mission", back_populates="zone")
    predictions = relationship("DemandPrediction", back_populates="zone")
    overrides = relationship("PriorityOverride", back_populates="zone")
    routes = relationship("RoutePlan", back_populates="zone")
    field_reports = relationship("FieldReport", back_populates="zone")


class ResourceDepot(Base):
    __tablename__ = "resource_depots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    location_name: Mapped[str] = mapped_column(String(255), nullable=False)
    latitude: Mapped[float] = mapped_column(Float, nullable=False)
    longitude: Mapped[float] = mapped_column(Float, nullable=False)
    capacity: Mapped[int] = mapped_column(Integer, default=10000)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    resources = relationship("Resource", back_populates="depot", cascade="all, delete-orphan")
    routes = relationship("RoutePlan", back_populates="depot")


class Resource(Base):
    __tablename__ = "resources"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("resource_depots.id", ondelete="CASCADE"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity_available: Mapped[float] = mapped_column(Float, default=0.0)
    quantity_reserved: Mapped[float] = mapped_column(Float, default=0.0)
    quantity_deployed: Mapped[float] = mapped_column(Float, default=0.0)
    unit: Mapped[str] = mapped_column(String(50), default="units")
    status: Mapped[ResourceStatus] = mapped_column(Enum(ResourceStatus), default=ResourceStatus.AVAILABLE)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    depot = relationship("ResourceDepot", back_populates="resources")
    allocations = relationship("ResourceAllocation", back_populates="resource")


class ResourceAllocation(Base):
    __tablename__ = "resource_allocations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    resource_id: Mapped[int] = mapped_column(ForeignKey("resources.id", ondelete="CASCADE"), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(100), nullable=False)
    requested_quantity: Mapped[float] = mapped_column(Float, default=0.0)
    allocated_quantity: Mapped[float] = mapped_column(Float, default=0.0)
    shortage: Mapped[float] = mapped_column(Float, default=0.0)
    coverage_pct: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    zone = relationship("DisasterZone", back_populates="allocations")
    resource = relationship("Resource", back_populates="allocations")


class FieldTeam(Base):
    __tablename__ = "field_teams"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    leader_name: Mapped[str] = mapped_column(String(255), nullable=False)
    members_count: Mapped[int] = mapped_column(Integer, default=5)
    skills: Mapped[str | None] = mapped_column(Text)
    latitude: Mapped[float] = mapped_column(Float, default=0.0)
    longitude: Mapped[float] = mapped_column(Float, default=0.0)
    status: Mapped[TeamStatus] = mapped_column(Enum(TeamStatus), default=TeamStatus.AVAILABLE)
    assigned_disaster_id: Mapped[int | None] = mapped_column(ForeignKey("disasters.id", ondelete="SET NULL"))

    missions = relationship("Mission", back_populates="team")


class Mission(Base):
    __tablename__ = "missions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    disaster_id: Mapped[int] = mapped_column(ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    team_id: Mapped[int] = mapped_column(ForeignKey("field_teams.id", ondelete="CASCADE"), nullable=False)
    assigned_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    resources_json: Mapped[dict | None] = mapped_column(JSON)
    priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), default=PriorityLevel.MEDIUM)
    status: Mapped[MissionStatus] = mapped_column(Enum(MissionStatus), default=MissionStatus.PLANNED)
    deadline: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow, onupdate=utcnow)

    disaster = relationship("Disaster", back_populates="missions")
    zone = relationship("DisasterZone", back_populates="missions")
    team = relationship("FieldTeam", back_populates="missions")
    assigned_by_user = relationship("User", back_populates="missions_led", foreign_keys=[assigned_by])


class DemandPrediction(Base):
    __tablename__ = "demand_predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_id: Mapped[int] = mapped_column(ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    food_demand: Mapped[float] = mapped_column(Float, default=0.0)
    water_demand_litres: Mapped[float] = mapped_column(Float, default=0.0)
    medical_kit_demand: Mapped[float] = mapped_column(Float, default=0.0)
    shelter_demand: Mapped[float] = mapped_column(Float, default=0.0)
    base_food: Mapped[float] = mapped_column(Float, default=0.0)
    base_water: Mapped[float] = mapped_column(Float, default=0.0)
    base_medical: Mapped[float] = mapped_column(Float, default=0.0)
    base_shelter: Mapped[float] = mapped_column(Float, default=0.0)
    vulnerability_adjustment: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[dict | None] = mapped_column(JSON)
    model_used: Mapped[dict | None] = mapped_column(JSON)
    reason: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    disaster = relationship("Disaster", back_populates="predictions")
    zone = relationship("DisasterZone", back_populates="predictions")


class FieldReport(Base):
    __tablename__ = "field_reports"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    reporter_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    population_affected: Mapped[int | None] = mapped_column(Integer)
    building_damage_pct: Mapped[float | None] = mapped_column(Float)
    road_damage_pct: Mapped[float | None] = mapped_column(Float)
    severity: Mapped[PriorityLevel | None] = mapped_column(Enum(PriorityLevel))
    accessibility_score: Mapped[float | None] = mapped_column(Float)
    notes: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    zone = relationship("DisasterZone", back_populates="field_reports")
    reporter = relationship("User", back_populates="field_reports")


class PriorityOverride(Base):
    __tablename__ = "priority_overrides"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    previous_priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), nullable=False)
    new_priority: Mapped[PriorityLevel] = mapped_column(Enum(PriorityLevel), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    changed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    zone = relationship("DisasterZone", back_populates="overrides")
    changed_by_user = relationship("User", back_populates="priority_overrides")


class Scenario(Base):
    __tablename__ = "scenarios"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    disaster_id: Mapped[int] = mapped_column(ForeignKey("disasters.id", ondelete="CASCADE"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    response_speed: Mapped[str] = mapped_column(String(50), default="normal")
    available_food: Mapped[float] = mapped_column(Float, default=0.0)
    available_water: Mapped[float] = mapped_column(Float, default=0.0)
    available_medical: Mapped[float] = mapped_column(Float, default=0.0)
    available_shelter: Mapped[float] = mapped_column(Float, default=0.0)
    transport_capacity: Mapped[float] = mapped_column(Float, default=0.0)
    results_json: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    disaster = relationship("Disaster", back_populates="scenarios")


class RoutePlan(Base):
    __tablename__ = "routes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    depot_id: Mapped[int] = mapped_column(ForeignKey("resource_depots.id", ondelete="CASCADE"), nullable=False)
    zone_id: Mapped[int] = mapped_column(ForeignKey("disaster_zones.id", ondelete="CASCADE"), nullable=False)
    distance_km: Mapped[float] = mapped_column(Float, default=0.0)
    estimated_time_hours: Mapped[float] = mapped_column(Float, default=0.0)
    vehicle_type: Mapped[str] = mapped_column(String(100), default="truck")
    resources_json: Mapped[dict | None] = mapped_column(JSON)
    route_geometry: Mapped[dict | None] = mapped_column(JSON)
    provider: Mapped[str] = mapped_column(String(50), default="local_haversine")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    depot = relationship("ResourceDepot", back_populates="routes")
    zone = relationship("DisasterZone", back_populates="routes")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"))
    action: Mapped[str] = mapped_column(String(255), nullable=False)
    entity_type: Mapped[str | None] = mapped_column(String(100))
    entity_id: Mapped[int | None] = mapped_column(Integer)
    details: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    user = relationship("User", back_populates="audit_logs")
