"""Standalone prediction helper for trained models."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

import joblib
import pandas as pd

from preprocessing import TARGETS

ROOT = Path(__file__).resolve().parent
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

TARGET_SLUGS = {
    "food_demand": "food",
    "water_demand_litres": "water",
    "medical_kit_demand": "medical",
    "shelter_demand": "shelter",
}


def load_best_models() -> Dict[str, Any]:
    path = RESULTS_DIR / "best_models.json"
    if not path.exists():
        raise FileNotFoundError("best_models.json not found. Run train_models.py first.")
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def predict_row(features: dict) -> dict:
    preprocessor = joblib.load(MODELS_DIR / "preprocessor.pkl")
    best = load_best_models()["best_models"]
    frame = pd.DataFrame([features])
    # Align columns expected by preprocessor if possible
    config_path = MODELS_DIR / "preprocessor_config.json"
    if config_path.exists():
        with open(config_path, encoding="utf-8") as f:
            cfg = json.load(f)
        for col in cfg.get("feature_columns", []):
            if col not in frame.columns:
                frame[col] = 0
        frame = frame[cfg["feature_columns"]]

    Xt = preprocessor.transform(frame)
    out = {}
    models_used = {}
    for target in TARGETS:
        info = best[target]
        model = joblib.load(MODELS_DIR / info["model_file"])
        pred = float(model.predict(Xt)[0])
        out[target] = max(0.0, pred)
        models_used[target] = info["model"]
    out["models_used"] = models_used
    return out


if __name__ == "__main__":
    sample = {
        "latitude": 13.6288,
        "longitude": 79.4192,
        "population": 50000,
        "population_density": 1200,
        "vulnerability_score": 0.72,
        "severity_score": 0.85,
        "building_damage_pct": 35,
        "road_damage_pct": 20,
        "rainfall": 150,
        "humidity": 80,
        "elderly_pct": 0.12,
        "children_pct": 0.22,
        "medical_dependency_pct": 0.08,
        "accessibility_score": 0.7,
        "disaster_type": "Flood",
        "subtype": "Riverine",
        "year": 2024,
        "month": 9,
        "day": 13,
        "day_of_week": 4,
        "day_of_year": 257,
    }
    print(predict_row(sample))
