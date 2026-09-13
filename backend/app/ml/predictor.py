"""ML prediction service loaded from trained resource_demand_ml_ready models."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd

from app.config import get_settings

logger = logging.getLogger(__name__)

TARGETS = [
    "food_demand",
    "water_demand_litres",
    "medical_kit_demand",
    "shelter_demand",
]

TARGET_KEYS = {
    "food_demand": "food",
    "water_demand_litres": "water",
    "medical_kit_demand": "medical",
    "shelter_demand": "shelter",
}


class DemandPredictor:
    def __init__(self) -> None:
        self.ready = False
        self.preprocessor = None
        self.models: Dict[str, Any] = {}
        self.best: Dict[str, Any] = {}
        self.feature_columns: list[str] = []
        self.results_summary: list[dict] = []
        self.error: Optional[str] = None
        self.dataset_info: Dict[str, Any] = {}

    def _resolve_dirs(self) -> tuple[Path, Path]:
        settings = get_settings()
        models_dir = Path(settings.ml_models_dir)
        results_dir = Path(settings.ml_results_dir)
        if not models_dir.is_absolute():
            models_dir = (Path.cwd() / models_dir).resolve()
        if not results_dir.is_absolute():
            results_dir = (Path.cwd() / results_dir).resolve()
        if not models_dir.exists():
            models_dir = Path(__file__).resolve().parents[3] / "ml" / "models"
        if not results_dir.exists():
            results_dir = Path(__file__).resolve().parents[3] / "ml" / "results"
        return models_dir, results_dir

    def load(self) -> None:
        models_dir, results_dir = self._resolve_dirs()
        pre_path = models_dir / "preprocessor.pkl"
        best_path = results_dir / "best_models.json"
        if not pre_path.exists() or not best_path.exists():
            self.error = "Trained models not found. Run: cd ml && python train_models.py"
            logger.warning(self.error)
            return

        # Pickled objects were saved from the ml/ package; ensure import path exists
        import sys

        ml_root = models_dir.parent
        if str(ml_root) not in sys.path:
            sys.path.insert(0, str(ml_root))

        try:
            self.preprocessor = joblib.load(pre_path)
            with open(best_path, encoding="utf-8") as f:
                payload = json.load(f)
            self.best = payload.get("best_models", {})
            self.dataset_info = {
                "dataset": payload.get("dataset"),
                "n_rows": payload.get("n_rows"),
                "note": payload.get("note"),
            }

            cfg_path = models_dir / "preprocessor_config.json"
            if cfg_path.exists():
                with open(cfg_path, encoding="utf-8") as f:
                    cfg = json.load(f)
                self.feature_columns = cfg.get("feature_columns", [])

            for target, info in self.best.items():
                model_file = models_dir / info["model_file"]
                if model_file.exists():
                    self.models[target] = joblib.load(model_file)

            results_csv = results_dir / "model_results.csv"
            if results_csv.exists():
                df = pd.read_csv(results_csv)
                records = []
                for _, row in df.iterrows():
                    records.append(
                        {
                            "model": row.get("Model", row.get("model")),
                            "target": row.get("Target", row.get("target")),
                            "train_r2": row.get("train_r2", (row.get("Train Accuracy (%)") or 0) / 100),
                            "test_r2": row.get("test_r2", row.get("R2 Score")),
                            "accuracy_r2_pct": row.get(
                                "accuracy_r2_pct", row.get("Test Accuracy (%)")
                            ),
                            "mae": row.get("mae", row.get("MAE")),
                            "rmse": row.get("rmse", row.get("RMSE")),
                            "mape": row.get("mape", row.get("MAPE (%)")),
                        }
                    )
                self.results_summary = records

            self.ready = bool(self.models)
            logger.info(
                "Loaded %s demand models from %s (dataset rows=%s)",
                len(self.models),
                models_dir,
                self.dataset_info.get("n_rows"),
            )
        except Exception as exc:
            self.ready = False
            self.error = f"Failed to load ML models: {exc}"
            logger.exception("ML model load failed")

    def predict_base(self, payload: dict) -> Dict[str, Any]:
        if not self.ready:
            raise RuntimeError(self.error or "ML models not loaded")

        if hasattr(self.preprocessor, "transform_payload"):
            Xt = self.preprocessor.transform_payload(payload)
        else:
            # Backward compatibility with older ColumnTransformer preprocessor
            frame = pd.DataFrame([payload])
            for col in self.feature_columns:
                if col not in frame.columns:
                    frame[col] = 0
            if self.feature_columns:
                frame = frame[self.feature_columns]
            Xt = self.preprocessor.transform(frame)

        preds = {}
        confidence = {}
        models_used = {}
        for target in TARGETS:
            model = self.models.get(target)
            if model is None:
                raise RuntimeError(f"No trained model for {target}")
            value = float(model.predict(Xt)[0])
            preds[target] = max(0.0, value)
            info = self.best.get(target, {})
            models_used[target] = info.get("model", "unknown")
            r2 = info.get("test_r2")
            confidence[TARGET_KEYS[target]] = (
                f"R2-based Accuracy (%) = {r2 * 100:.2f}" if r2 is not None else "n/a"
            )
        return {"predictions": preds, "confidence": confidence, "models_used": models_used}

    def apply_vulnerability(
        self,
        base: Dict[str, float],
        vulnerability_score: float,
        population: float = 0,
        population_density: float = 0,
        elderly_pct: float = 0.12,
        children_pct: float = 0.22,
        medical_dependency_pct: float = 0.08,
    ) -> Dict[str, Any]:
        vuln = float(np.clip(vulnerability_score, 0, 1))
        # Dataset stores children/elderly as percentages (e.g. 22.37), normalize if needed
        if elderly_pct > 1:
            elderly_pct = elderly_pct / 100.0
        if children_pct > 1:
            children_pct = children_pct / 100.0
        if medical_dependency_pct > 1:
            medical_dependency_pct = medical_dependency_pct / 100.0
        demo = 0.15 * elderly_pct + 0.1 * children_pct + 0.2 * medical_dependency_pct
        density_factor = min(0.15, max(0.0, (population_density - 500) / 10000))
        adjustment = 0.15 * vuln + demo + density_factor
        final = {k: float(v) * (1 + adjustment) for k, v in base.items()}
        return {
            "base_demand": base,
            "vulnerability_adjustment": round(adjustment, 4),
            "final_demand": final,
            "breakdown": {
                "vulnerability_component": round(0.15 * vuln, 4),
                "demographic_component": round(demo, 4),
                "density_component": round(density_factor, 4),
            },
        }

    def predict(self, payload: dict) -> Dict[str, Any]:
        base_result = self.predict_base(payload)
        vuln = self.apply_vulnerability(
            base_result["predictions"],
            vulnerability_score=float(payload.get("vulnerability_score", 0.5)),
            population=float(payload.get("population", 0)),
            population_density=float(payload.get("population_density", 0)),
            elderly_pct=float(payload.get("elderly_pct", payload.get("elderly_pct", 12))),
            children_pct=float(payload.get("children_pct", 22)),
            medical_dependency_pct=float(
                payload.get(
                    "medically_dependent_pct",
                    payload.get("medical_dependency_pct", 8),
                )
            ),
        )
        final = vuln["final_demand"]
        return {
            "food_demand": round(final["food_demand"], 2),
            "water_demand_litres": round(final["water_demand_litres"], 2),
            "medical_kit_demand": round(final["medical_kit_demand"], 2),
            "shelter_demand": round(final["shelter_demand"], 2),
            "confidence": base_result["confidence"],
            "models_used": base_result["models_used"],
            "base_demand": {k: round(v, 2) for k, v in vuln["base_demand"].items()},
            "vulnerability_adjustment": vuln["vulnerability_adjustment"],
            "vulnerability_breakdown": vuln["breakdown"],
            "formula": "Final Demand = Base Demand x (1 + Vulnerability Adjustment)",
            "dataset_rows": self.dataset_info.get("n_rows"),
        }


predictor = DemandPredictor()
