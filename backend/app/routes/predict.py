"""Demand prediction API routes."""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.ml.predictor import predictor
from app.models import DemandPrediction, DisasterZone, User, UserRole
from app.schemas.predict import DemandInput, DemandOutput, DemandUpdateInput, DemandUpdateOutput
from app.utils.deps import get_current_user, require_roles

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/predict", tags=["Prediction"])


def _pct_change(old: float, new: float) -> float:
    if old is None or abs(old) < 1e-9:
        return 100.0 if new else 0.0
    return round(((new - old) / old) * 100.0, 2)


def _normalize_payload(payload) -> dict:
    data = payload.model_dump()
    if not data.get("disaster_subtype"):
        data["disaster_subtype"] = data.get("subtype") or "River Flood"
    if data.get("medically_dependent_pct") is None:
        data["medically_dependent_pct"] = data.get("medical_dependency_pct")
    return data


@router.get("/status")
def prediction_status(_: User = Depends(get_current_user)):
    return {
        "ready": predictor.ready,
        "error": predictor.error,
        "models_loaded": list(predictor.models.keys()),
        "best_models": predictor.best,
        "dataset": predictor.dataset_info,
    }


@router.get("/metrics")
def model_metrics(_: User = Depends(get_current_user)):
    if not predictor.results_summary:
        raise HTTPException(
            status_code=404,
            detail="No metrics found. Train models with: python ml/train_models.py",
        )
    return {
        "note": "accuracy_r2_pct is R² × 100 (R²-based Accuracy %), not classification accuracy.",
        "results": predictor.results_summary,
        "best_models": predictor.best,
    }


@router.post("/demand", response_model=DemandOutput)
def predict_demand(
    payload: DemandInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN, UserRole.FIELD_TEAM)),
):
    if not predictor.ready:
        raise HTTPException(status_code=503, detail=predictor.error or "Models not loaded")
    try:
        result = predictor.predict(_normalize_payload(payload))
    except Exception as exc:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc

    if payload.zone_id:
        zone = db.get(DisasterZone, payload.zone_id)
        if zone:
            zone.food_demand = result["food_demand"]
            zone.water_demand_litres = result["water_demand_litres"]
            zone.medical_kit_demand = result["medical_kit_demand"]
            zone.shelter_demand = result["shelter_demand"]
            record = DemandPrediction(
                disaster_id=payload.disaster_id or zone.disaster_id,
                zone_id=zone.id,
                food_demand=result["food_demand"],
                water_demand_litres=result["water_demand_litres"],
                medical_kit_demand=result["medical_kit_demand"],
                shelter_demand=result["shelter_demand"],
                base_food=result["base_demand"]["food_demand"],
                base_water=result["base_demand"]["water_demand_litres"],
                base_medical=result["base_demand"]["medical_kit_demand"],
                base_shelter=result["base_demand"]["shelter_demand"],
                vulnerability_adjustment=result["vulnerability_adjustment"],
                confidence=result["confidence"],
                model_used=result["models_used"],
                reason="initial_prediction",
            )
            db.add(record)
            db.commit()

    logger.info("Demand predicted by user %s", user.id)
    return result


@router.post("/demand/update", response_model=DemandUpdateOutput)
def update_demand(
    payload: DemandUpdateInput,
    db: Session = Depends(get_db),
    user: User = Depends(require_roles(UserRole.RELIEF_COORDINATOR, UserRole.ADMIN)),
):
    if not predictor.ready:
        raise HTTPException(status_code=503, detail=predictor.error or "Models not loaded")

    previous = {
        "food_demand": payload.previous_food_demand,
        "water_demand_litres": payload.previous_water_demand_litres,
        "medical_kit_demand": payload.previous_medical_kit_demand,
        "shelter_demand": payload.previous_shelter_demand,
    }

    if payload.zone_id:
        zone = db.get(DisasterZone, payload.zone_id)
        if zone:
            previous = {
                "food_demand": previous["food_demand"] if previous["food_demand"] is not None else zone.food_demand,
                "water_demand_litres": previous["water_demand_litres"]
                if previous["water_demand_litres"] is not None
                else zone.water_demand_litres,
                "medical_kit_demand": previous["medical_kit_demand"]
                if previous["medical_kit_demand"] is not None
                else zone.medical_kit_demand,
                "shelter_demand": previous["shelter_demand"]
                if previous["shelter_demand"] is not None
                else zone.shelter_demand,
            }
            # Apply field updates onto zone attributes when provided via payload
            zone.population = int(payload.population)
            zone.population_density = payload.population_density
            zone.vulnerability_score = payload.vulnerability_score
            zone.building_damage_pct = payload.building_damage_pct
            zone.road_damage_pct = payload.road_damage_pct
            zone.rainfall = payload.rainfall
            zone.humidity = payload.humidity
            zone.accessibility_score = payload.accessibility_score

    try:
        result = predictor.predict(_normalize_payload(payload))
    except Exception as exc:
        logger.exception("Demand update failed")
        raise HTTPException(status_code=500, detail=f"Prediction error: {exc}") from exc

    percentage_change = {
        k: _pct_change(float(previous.get(k) or 0), float(result[k]))
        for k in ["food_demand", "water_demand_litres", "medical_kit_demand", "shelter_demand"]
    }

    if payload.zone_id:
        zone = db.get(DisasterZone, payload.zone_id)
        if zone:
            zone.food_demand = result["food_demand"]
            zone.water_demand_litres = result["water_demand_litres"]
            zone.medical_kit_demand = result["medical_kit_demand"]
            zone.shelter_demand = result["shelter_demand"]
            db.add(
                DemandPrediction(
                    disaster_id=payload.disaster_id or zone.disaster_id,
                    zone_id=zone.id,
                    food_demand=result["food_demand"],
                    water_demand_litres=result["water_demand_litres"],
                    medical_kit_demand=result["medical_kit_demand"],
                    shelter_demand=result["shelter_demand"],
                    base_food=result["base_demand"]["food_demand"],
                    base_water=result["base_demand"]["water_demand_litres"],
                    base_medical=result["base_demand"]["medical_kit_demand"],
                    base_shelter=result["base_demand"]["shelter_demand"],
                    vulnerability_adjustment=result["vulnerability_adjustment"],
                    confidence=result["confidence"],
                    model_used=result["models_used"],
                    reason=payload.reason,
                )
            )
            db.commit()

    return {
        **result,
        "previous_demand": {k: float(previous.get(k) or 0) for k in previous},
        "percentage_change": percentage_change,
        "reason": payload.reason,
    }
