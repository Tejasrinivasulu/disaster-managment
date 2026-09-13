"""Field report submission and listing."""

import logging
from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import DisasterZone, FieldReport, PriorityLevel, User, UserRole
from app.services.audit import write_audit
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/field-reports", tags=["Field Reports"])


class FieldReportCreate(BaseModel):
    zone_id: int
    mission_id: Optional[int] = None
    population_affected: Optional[int] = Field(default=None, ge=0)
    building_damage_pct: Optional[float] = Field(default=None, ge=0, le=100)
    road_damage_pct: Optional[float] = Field(default=None, ge=0, le=100)
    severity: Optional[PriorityLevel] = None
    accessibility_score: Optional[float] = Field(default=None, ge=0, le=1)
    notes: Optional[str] = None
    evidence_note: Optional[str] = None  # placeholder for upload metadata


class FieldReportOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    zone_id: int
    reporter_id: Optional[int]
    population_affected: Optional[int]
    building_damage_pct: Optional[float]
    road_damage_pct: Optional[float]
    severity: Optional[PriorityLevel]
    accessibility_score: Optional[float]
    notes: Optional[str]
    created_at: datetime


@router.get("", response_model=List[FieldReportOut])
def list_reports(
    zone_id: Optional[int] = None,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    q = db.query(FieldReport).order_by(FieldReport.created_at.desc())
    if zone_id is not None:
        q = q.filter(FieldReport.zone_id == zone_id)
    if user.role == UserRole.FIELD_TEAM:
        q = q.filter(FieldReport.reporter_id == user.id)
    return q.limit(200).all()


@router.post("", response_model=FieldReportOut, status_code=201)
def submit_report(
    payload: FieldReportCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.FIELD_TEAM, UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    zone = db.get(DisasterZone, payload.zone_id)
    if not zone:
        raise HTTPException(status_code=404, detail="Zone not found")

    notes = payload.notes or ""
    if payload.evidence_note:
        notes = (notes + f"\n[Evidence] {payload.evidence_note}").strip()
    if payload.mission_id:
        notes = (notes + f"\n[Mission #{payload.mission_id}]").strip()

    report = FieldReport(
        zone_id=payload.zone_id,
        reporter_id=user.id,
        population_affected=payload.population_affected,
        building_damage_pct=payload.building_damage_pct,
        road_damage_pct=payload.road_damage_pct,
        severity=payload.severity,
        accessibility_score=payload.accessibility_score,
        notes=notes or None,
    )
    db.add(report)

    # Apply field updates onto zone so coordinator sees latest ground truth
    if payload.population_affected is not None:
        zone.population = payload.population_affected
    if payload.building_damage_pct is not None:
        zone.building_damage_pct = payload.building_damage_pct
    if payload.road_damage_pct is not None:
        zone.road_damage_pct = payload.road_damage_pct
    if payload.accessibility_score is not None:
        zone.accessibility_score = payload.accessibility_score
    if payload.severity is not None:
        zone.severity = payload.severity

    db.commit()
    db.refresh(report)
    write_audit(
        db,
        user_id=user.id,
        action="field_report.submit",
        entity_type="field_report",
        entity_id=report.id,
        details=f"Zone {zone.id}: pop={payload.population_affected}, damage={payload.building_damage_pct}",
    )
    logger.info("Field report %s by user %s for zone %s", report.id, user.id, zone.id)
    return report
