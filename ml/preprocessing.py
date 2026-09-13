"""Preprocessing aligned with resource_demand_ml_ready.csv training pipeline."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.impute import SimpleImputer
from sklearn.model_selection import train_test_split

TARGETS = [
    "food_demand",
    "water_demand_litres",
    "medical_kit_demand",
    "shelter_demand",
]


class DemandPreprocessor:
    """
    Matches the user algorithm:
    - date → year/month/day/dayofweek/dayofyear
    - drop all target columns (no leakage)
    - categorical → category codes
    - replace inf with nan
    - median impute
    Fit only on training rows, then apply to test / live inference.
    """

    def __init__(self):
        self.feature_columns: List[str] = []
        self.categorical_columns: List[str] = []
        self.category_maps: Dict[str, Dict[str, int]] = {}
        self.category_defaults: Dict[str, str] = {}
        self.imputer: SimpleImputer | None = None
        self.feature_medians: Dict[str, float] = {}

    def _engineer_dates(self, df: pd.DataFrame) -> pd.DataFrame:
        out = df.copy()
        if "date" in out.columns:
            parsed = pd.to_datetime(out["date"], errors="coerce")
            out["year"] = parsed.dt.year
            out["month"] = parsed.dt.month
            out["day"] = parsed.dt.day
            out["dayofweek"] = parsed.dt.dayofweek
            out["dayofyear"] = parsed.dt.dayofyear
            out = out.drop(columns=["date"])
        return out

    def _encode_categoricals(self, df: pd.DataFrame, fit: bool) -> pd.DataFrame:
        out = df.copy()
        if fit:
            self.categorical_columns = out.select_dtypes(include=["object", "category"]).columns.tolist()
            self.category_maps = {}
            self.category_defaults = {}
            for col in self.categorical_columns:
                series = out[col].astype("object").fillna("__MISSING__").astype(str)
                cats = sorted(series.unique())
                mapping = {str(v): i for i, v in enumerate(cats)}
                self.category_maps[col] = mapping
                mode_val = series.mode()
                self.category_defaults[col] = str(mode_val.iloc[0]) if len(mode_val) else cats[0]
                out[col] = series.map(mapping).fillna(-1)
        else:
            for col in self.categorical_columns:
                mapping = self.category_maps.get(col, {})
                if col not in out.columns:
                    out[col] = -1
                else:
                    out[col] = (
                        out[col]
                        .astype("object")
                        .fillna("__MISSING__")
                        .astype(str)
                        .map(mapping)
                        .fillna(-1)
                    )
        return out

    def fit(self, X: pd.DataFrame) -> "DemandPreprocessor":
        X = self._engineer_dates(X)
        X = X.drop(columns=[c for c in TARGETS if c in X.columns], errors="ignore")
        X = self._encode_categoricals(X, fit=True)
        X = X.replace([np.inf, -np.inf], np.nan)
        self.feature_columns = list(X.columns)
        self.feature_medians = {
            c: float(X[c].median()) if pd.api.types.is_numeric_dtype(X[c]) else 0.0
            for c in self.feature_columns
        }
        self.imputer = SimpleImputer(strategy="median")
        self.imputer.fit(X[self.feature_columns])
        return self

    def transform(self, X: pd.DataFrame) -> np.ndarray:
        X = self._engineer_dates(X)
        X = X.drop(columns=[c for c in TARGETS if c in X.columns], errors="ignore")
        X = self._encode_categoricals(X, fit=False)
        X = X.replace([np.inf, -np.inf], np.nan)
        for col in self.feature_columns:
            if col not in X.columns:
                X[col] = self.feature_medians.get(col, 0.0)
        X = X[self.feature_columns]
        return self.imputer.transform(X)

    def fit_transform(self, X: pd.DataFrame) -> np.ndarray:
        self.fit(X)
        return self.transform(X)

    def transform_payload(self, payload: dict) -> np.ndarray:
        """Build one inference row from API payload; missing fields use training defaults."""
        row: Dict[str, Any] = {}
        for col in self.feature_columns:
            if col in self.categorical_columns:
                continue
            row[col] = self.feature_medians.get(col, 0.0)
        for col in self.categorical_columns:
            row[col] = self.category_defaults.get(col, "__MISSING__")

        aliases = {
            "day_of_week": "dayofweek",
            "day_of_year": "dayofyear",
            "medical_dependency_pct": "medically_dependent_pct",
            "subtype": "disaster_subtype",
        }
        for key, value in payload.items():
            if value is None:
                continue
            key2 = aliases.get(key, key)
            if key2 in self.feature_columns or key2 in ("date",):
                row[key2] = value
            elif key in self.feature_columns:
                row[key] = value

        if payload.get("date"):
            row["date"] = payload["date"]

        frame = pd.DataFrame([row])
        return self.transform(frame)


def find_dataset(data_dir: Path) -> Path:
    preferred = [
        data_dir / "resource_demand_ml_ready.csv",
        data_dir / "disaster_demand_dataset.csv",
    ]
    for path in preferred:
        if path.exists():
            return path
    csvs = sorted(p for p in data_dir.glob("*.csv") if p.stat().st_size > 1000)
    if not csvs:
        raise FileNotFoundError(f"No CSV found in {data_dir}")
    return csvs[0]


def prepare_data(
    data_dir: Path,
    test_size: float = 0.2,
    random_state: int = 42,
) -> Dict[str, Any]:
    path = find_dataset(data_dir)
    print(f"Loading {path} …")
    df = pd.read_csv(path)
    print(f"Rows: {df.shape[0]:,}  Columns: {df.shape[1]}")
    print("Targets:", TARGETS)

    missing = [t for t in TARGETS if t not in df.columns]
    if missing:
        raise ValueError(f"Missing target columns: {missing}")

    y = df[TARGETS].copy()
    X = df.drop(columns=TARGETS)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    preprocessor = DemandPreprocessor()
    X_train_t = preprocessor.fit_transform(X_train)
    X_test_t = preprocessor.transform(X_test)

    config = {
        "dataset": str(path),
        "n_rows": int(len(df)),
        "n_features_raw": int(X.shape[1]),
        "feature_columns": preprocessor.feature_columns,
        "categorical_columns": preprocessor.categorical_columns,
        "targets": TARGETS,
        "test_size": test_size,
        "random_state": random_state,
        "feature_medians": preprocessor.feature_medians,
    }
    return {
        "df": df,
        "X_train": X_train_t,
        "X_test": X_test_t,
        "y_train": y_train,
        "y_test": y_test,
        "preprocessor": preprocessor,
        "config": config,
    }


def save_preprocessor(preprocessor: DemandPreprocessor, config: dict, models_dir: Path) -> None:
    models_dir.mkdir(parents=True, exist_ok=True)
    joblib.dump(preprocessor, models_dir / "preprocessor.pkl")
    with open(models_dir / "preprocessor_config.json", "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, default=str)
