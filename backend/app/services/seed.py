"""Seed demo users and sample operational data."""

import logging

from sqlalchemy.orm import Session

from app.models import (
    Disaster,
    DisasterStatus,
    DisasterZone,
    FieldTeam,
    PriorityLevel,
    Resource,
    ResourceDepot,
    ResourceStatus,
    TeamStatus,
    User,
    UserRole,
)
from app.utils.security import hash_password

logger = logging.getLogger(__name__)

DEMO_USERS = [
    {
        "email": "admin@disaster.local",
        "full_name": "System Admin",
        "password": "admin123",
        "role": UserRole.ADMIN,
    },
    {
        "email": "coordinator@disaster.local",
        "full_name": "Relief Coordinator",
        "password": "coord123",
        "role": UserRole.RELIEF_COORDINATOR,
    },
    {
        "email": "field@disaster.local",
        "full_name": "Field Team Lead",
        "password": "field123",
        "role": UserRole.FIELD_TEAM,
    },
]


def seed_database(db: Session) -> None:
    if db.query(User).count() == 0:
        for u in DEMO_USERS:
            db.add(
                User(
                    email=u["email"],
                    full_name=u["full_name"],
                    hashed_password=hash_password(u["password"]),
                    role=u["role"],
                )
            )
        db.commit()
        logger.info("Seeded demo users")

    if db.query(Disaster).count() == 0:
        flood = Disaster(
            disaster_type="Flood",
            subtype="Riverine",
            title="Tirupati District Flood Event",
            description="Heavy monsoon rainfall caused river overflow affecting multiple mandals.",
            location_name="Tirupati, Andhra Pradesh",
            latitude=13.6288,
            longitude=79.4192,
            severity=PriorityLevel.HIGH,
            status=DisasterStatus.ACTIVE,
            affected_population=125000,
        )
        quake = Disaster(
            disaster_type="Earthquake",
            subtype="Moderate",
            title="Coastal Andhra Seismic Tremor",
            description="Moderate tremor with localized structural damage.",
            location_name="Nellore, Andhra Pradesh",
            latitude=14.4426,
            longitude=79.9865,
            severity=PriorityLevel.MEDIUM,
            status=DisasterStatus.MONITORING,
            affected_population=42000,
        )
        db.add_all([flood, quake])
        db.flush()

        zones = [
            DisasterZone(
                disaster_id=flood.id,
                name="Zone A — Chandragiri",
                latitude=13.5845,
                longitude=79.3120,
                population=50000,
                population_density=1200,
                vulnerability_score=0.72,
                accessibility_score=0.85,
                building_damage_pct=35,
                road_damage_pct=20,
                rainfall=150,
                humidity=80,
                severity=PriorityLevel.HIGH,
                priority=PriorityLevel.HIGH,
            ),
            DisasterZone(
                disaster_id=flood.id,
                name="Zone B — Renigunta",
                latitude=13.6510,
                longitude=79.5150,
                population=38000,
                population_density=980,
                vulnerability_score=0.65,
                accessibility_score=0.70,
                building_damage_pct=28,
                road_damage_pct=40,
                rainfall=140,
                humidity=82,
                severity=PriorityLevel.CRITICAL,
                priority=PriorityLevel.CRITICAL,
            ),
            DisasterZone(
                disaster_id=flood.id,
                name="Zone C — Srikalahasti",
                latitude=13.7500,
                longitude=79.7000,
                population=37000,
                population_density=850,
                vulnerability_score=0.58,
                accessibility_score=0.60,
                building_damage_pct=22,
                road_damage_pct=30,
                rainfall=130,
                humidity=78,
                severity=PriorityLevel.MEDIUM,
                priority=PriorityLevel.MEDIUM,
            ),
            DisasterZone(
                disaster_id=quake.id,
                name="Zone D — Nellore Urban",
                latitude=14.4426,
                longitude=79.9865,
                population=42000,
                population_density=2100,
                vulnerability_score=0.55,
                accessibility_score=0.90,
                building_damage_pct=15,
                road_damage_pct=8,
                rainfall=20,
                humidity=65,
                severity=PriorityLevel.MEDIUM,
                priority=PriorityLevel.MEDIUM,
            ),
        ]
        db.add_all(zones)

        depots = [
            ResourceDepot(
                name="Central Relief Depot Tirupati",
                location_name="Tirupati",
                latitude=13.6400,
                longitude=79.4200,
                capacity=50000,
            ),
            ResourceDepot(
                name="Coastal Staging Depot Nellore",
                location_name="Nellore",
                latitude=14.4500,
                longitude=79.9800,
                capacity=30000,
            ),
        ]
        db.add_all(depots)
        db.flush()

        resources = [
            Resource(
                depot_id=depots[0].id,
                resource_type="food_packets",
                name="Food Packets",
                quantity_available=25000,
                unit="packets",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[0].id,
                resource_type="water",
                name="Drinking Water",
                quantity_available=500000,
                unit="litres",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[0].id,
                resource_type="medical_kits",
                name="Medical Kits",
                quantity_available=5000,
                unit="kits",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[0].id,
                resource_type="shelter",
                name="Shelter Capacity",
                quantity_available=8000,
                unit="beds",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[0].id,
                resource_type="vehicles",
                name="Rescue Vehicles",
                quantity_available=12,
                unit="vehicles",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[0].id,
                resource_type="personnel",
                name="Relief Personnel",
                quantity_available=80,
                unit="people",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[1].id,
                resource_type="food_packets",
                name="Food Packets",
                quantity_available=10000,
                unit="packets",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[1].id,
                resource_type="water",
                name="Drinking Water",
                quantity_available=200000,
                unit="litres",
                status=ResourceStatus.AVAILABLE,
            ),
            Resource(
                depot_id=depots[1].id,
                resource_type="medical_kits",
                name="Medical Kits",
                quantity_available=2000,
                unit="kits",
                status=ResourceStatus.AVAILABLE,
            ),
        ]
        db.add_all(resources)

        teams = [
            FieldTeam(
                name="Alpha Rescue",
                leader_name="Ravi Kumar",
                members_count=8,
                skills="search_rescue,first_aid,boat_ops",
                latitude=13.6300,
                longitude=79.4300,
                status=TeamStatus.AVAILABLE,
            ),
            FieldTeam(
                name="Bravo Medical",
                leader_name="Dr. Priya Nair",
                members_count=6,
                skills="emergency_medicine,triage",
                latitude=13.6450,
                longitude=79.4100,
                status=TeamStatus.AVAILABLE,
            ),
            FieldTeam(
                name="Charlie Logistics",
                leader_name="Suresh Reddy",
                members_count=5,
                skills="transport,warehouse",
                latitude=14.4400,
                longitude=79.9900,
                status=TeamStatus.AVAILABLE,
            ),
        ]
        db.add_all(teams)
        db.commit()
        logger.info("Seeded demo disasters, zones, depots, resources, and teams")
