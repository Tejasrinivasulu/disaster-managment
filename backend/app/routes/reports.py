"""Scenario simulation and reports routes."""

import csv
import io
import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import (
    Disaster,
    DisasterZone,
    Mission,
    Resource,
    ResourceAllocation,
    Scenario,
    User,
    UserRole,
)
from app.schemas.ops import ScenarioCreate
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
scenarios_router = APIRouter(prefix="/scenarios", tags=["Scenarios"])
reports_router = APIRouter(prefix="/reports", tags=["Reports"])


def _run_scenario(zones: list[DisasterZone], payload: ScenarioCreate) -> dict:
    speed_factor = {"fast": 0.9, "normal": 1.0, "limited": 1.2}.get(payload.response_speed, 1.0)
    demands = {
        "food": sum((z.food_demand or z.population * 0.3) * speed_factor for z in zones),
        "water": sum((z.water_demand_litres or z.population * 15) * speed_factor for z in zones),
        "medical": sum((z.medical_kit_demand or z.population * 0.03) * speed_factor for z in zones),
        "shelter": sum((z.shelter_demand or z.population * 0.12) * speed_factor for z in zones),
    }
    available = {
        "food": payload.available_food,
        "water": payload.available_water,
        "medical": payload.available_medical,
        "shelter": payload.available_shelter,
    }
    shortage = {k: max(0.0, demands[k] - available[k]) for k in demands}
    coverage = {
        k: round(min(100.0, (available[k] / demands[k] * 100) if demands[k] else 100), 2)
        for k in demands
    }
    # Priority zones: highest severity/vulnerability first
    priority_zones = sorted(
        [
            {
                "id": z.id,
                "name": z.name,
                "priority": z.priority.value if hasattr(z.priority, "value") else z.priority,
                "vulnerability_score": z.vulnerability_score,
                "population": z.population,
            }
            for z in zones
        ],
        key=lambda x: (
            {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(str(x["priority"]), 9),
            -x["vulnerability_score"],
        ),
    )
    transport_limited = payload.transport_capacity > 0 and payload.transport_capacity < sum(available.values())
    return {
        "predicted_demand": {k: round(v, 2) for k, v in demands.items()},
        "available_resources": available,
        "shortage": {k: round(v, 2) for k, v in shortage.items()},
        "coverage_percentage": coverage,
        "priority_zones": priority_zones,
        "transport_capacity": payload.transport_capacity,
        "transport_constrained": transport_limited,
        "response_speed": payload.response_speed,
    }


@scenarios_router.get("")
def list_scenarios(db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    rows = db.query(Scenario).order_by(Scenario.created_at.desc()).all()
    return [
        {
            "id": s.id,
            "disaster_id": s.disaster_id,
            "name": s.name,
            "response_speed": s.response_speed,
            "available_food": s.available_food,
            "available_water": s.available_water,
            "available_medical": s.available_medical,
            "available_shelter": s.available_shelter,
            "transport_capacity": s.transport_capacity,
            "results_json": s.results_json,
            "created_at": s.created_at,
        }
        for s in rows
    ]


@scenarios_router.post("")
def create_scenario(
    payload: ScenarioCreate,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    if not db.get(Disaster, payload.disaster_id):
        raise HTTPException(status_code=404, detail="Disaster not found")
    zones = db.query(DisasterZone).filter(DisasterZone.disaster_id == payload.disaster_id).all()
    results = _run_scenario(zones, payload)
    scenario = Scenario(
        disaster_id=payload.disaster_id,
        name=payload.name,
        response_speed=payload.response_speed,
        available_food=payload.available_food,
        available_water=payload.available_water,
        available_medical=payload.available_medical,
        available_shelter=payload.available_shelter,
        transport_capacity=payload.transport_capacity,
        results_json=results,
    )
    db.add(scenario)
    db.commit()
    db.refresh(scenario)
    logger.info("Scenario %s created by %s", scenario.id, user.id)
    return {"id": scenario.id, "name": scenario.name, "results": results}


def build_report_summary(db: Session, disaster_id: int | None = None) -> dict:
    dq = db.query(Disaster)
    if disaster_id:
        dq = dq.filter(Disaster.id == disaster_id)
    disasters = dq.all()
    zq = db.query(DisasterZone)
    if disaster_id:
        zq = zq.filter(DisasterZone.disaster_id == disaster_id)
    zones = zq.all()
    allocations = db.query(ResourceAllocation).all()
    if disaster_id:
        zone_ids = {z.id for z in zones}
        allocations = [a for a in allocations if a.zone_id in zone_ids]
    missions = db.query(Mission).all()
    if disaster_id:
        missions = [m for m in missions if m.disaster_id == disaster_id]
    resources = db.query(Resource).all()

    total_requested = sum(a.requested_quantity for a in allocations)
    total_allocated = sum(a.allocated_quantity for a in allocations)
    total_shortage = sum(a.shortage for a in allocations)
    return {
        "total_affected_population": sum(d.affected_population for d in disasters),
        "disaster_count": len(disasters),
        "zone_count": len(zones),
        "total_resources_requested": round(total_requested, 2),
        "total_resources_allocated": round(total_allocated, 2),
        "total_shortages": round(total_shortage, 2),
        "zone_coverage_pct": round(
            (total_allocated / total_requested * 100) if total_requested else 0, 2
        ),
        "field_missions": len(missions),
        "missions_completed": sum(1 for m in missions if m.status.value == "completed"),
        "resource_utilization_pct": round(
            (
                sum(r.quantity_deployed for r in resources)
                / max(
                    1,
                    sum(
                        r.quantity_available + r.quantity_reserved + r.quantity_deployed
                        for r in resources
                    ),
                )
            )
            * 100,
            2,
        ),
        "disasters": [
            {
                "id": d.id,
                "title": d.title,
                "severity": d.severity.value if hasattr(d.severity, "value") else d.severity,
                "status": d.status.value if hasattr(d.status, "value") else d.status,
                "affected_population": d.affected_population,
            }
            for d in disasters
        ],
    }


@reports_router.get("/summary")
def report_summary(
    disaster_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    return build_report_summary(db, disaster_id)


@reports_router.get("/export.csv")
def export_csv(
    disaster_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    summary = build_report_summary(db, disaster_id)
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow(["metric", "value"])
    for key, value in summary.items():
        if key in ("disasters",):
            continue
        writer.writerow([key, value])
    buf.seek(0)
    return StreamingResponse(
        iter([buf.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=disaster_report.csv"},
    )


@reports_router.get("/export.pdf")
def export_pdf(
    disaster_id: int | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
):
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

    summary = build_report_summary(db, disaster_id)
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, title="Disaster Response Report")
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Disaster Response Management Report", styles["Title"]),
        Paragraph("Post-event analytics and resource utilization summary", styles["Normal"]),
        Spacer(1, 16),
    ]

    metrics = [
        ["Metric", "Value"],
        ["Affected Population", summary["total_affected_population"]],
        ["Disaster Count", summary["disaster_count"]],
        ["Zone Count", summary["zone_count"]],
        ["Resources Requested", summary["total_resources_requested"]],
        ["Resources Allocated", summary["total_resources_allocated"]],
        ["Total Shortages", summary["total_shortages"]],
        ["Zone Coverage %", summary["zone_coverage_pct"]],
        ["Field Missions", summary["field_missions"]],
        ["Missions Completed", summary["missions_completed"]],
        ["Resource Utilization %", summary["resource_utilization_pct"]],
    ]
    table = Table(metrics, colWidths=[280, 180])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#243b53")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 6),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    story.append(table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("Disasters", styles["Heading2"]))

    disaster_rows = [["ID", "Title", "Severity", "Status", "Affected"]]
    for d in summary["disasters"]:
        disaster_rows.append(
            [d["id"], d["title"], d["severity"], d["status"], d["affected_population"]]
        )
    dtable = Table(disaster_rows, colWidths=[40, 200, 70, 80, 70])
    dtable.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#334e68")),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, -1), 9),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
                ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f7fafc")]),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    story.append(dtable)
    doc.build(story)
    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=disaster_report.pdf"},
    )
