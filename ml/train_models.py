"""
Train 5 regressors on resource_demand_ml_ready.csv
using the project demand-prediction algorithm.

Targets (never used as features):
  food_demand, water_demand_litres, medical_kit_demand, shelter_demand

Metrics: R2, MAE, RMSE, MAPE
R2-based Accuracy (%) = Test R2 * 100
Best model per target selected by Test R2.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import (
    ExtraTreesRegressor,
    HistGradientBoostingRegressor,
    RandomForestRegressor,
)
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from xgboost import XGBRegressor

from preprocessing import TARGETS, prepare_data, save_preprocessor

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
MODELS_DIR = ROOT / "models"
RESULTS_DIR = ROOT / "results"

MODEL_SLUGS = {
    "XGBoost": "xgboost",
    "Random Forest": "random_forest",
    "Extra Trees": "extra_trees",
    "HistGradientBoosting": "hist_gradient",
    "Linear Regression": "linear",
}

TARGET_SLUGS = {
    "food_demand": "food",
    "water_demand_litres": "water",
    "medical_kit_demand": "medical",
    "shelter_demand": "shelter",
}


def mape_score(y_true, y_pred) -> float:
    y_true = np.asarray(y_true, dtype=float)
    y_pred = np.asarray(y_pred, dtype=float)
    mask = y_true != 0
    if mask.sum() == 0:
        return float("nan")
    return float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)


def make_model(name: str):
    if name == "XGBoost":
        return XGBRegressor(
            n_estimators=200,
            max_depth=8,
            learning_rate=0.05,
            subsample=0.8,
            colsample_bytree=0.8,
            objective="reg:squarederror",
            eval_metric="rmse",
            random_state=42,
            n_jobs=-1,
        )
    if name == "Random Forest":
        return RandomForestRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
    if name == "Extra Trees":
        return ExtraTreesRegressor(
            n_estimators=100,
            max_depth=20,
            min_samples_leaf=2,
            random_state=42,
            n_jobs=-1,
        )
    if name == "HistGradientBoosting":
        return HistGradientBoostingRegressor(
            max_iter=150,
            learning_rate=0.08,
            max_leaf_nodes=31,
            random_state=42,
        )
    return Pipeline(
        [
            ("scaler", StandardScaler()),
            ("regressor", LinearRegression()),
        ]
    )


def main():
    MODELS_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    data = prepare_data(DATA_DIR)
    save_preprocessor(data["preprocessor"], data["config"], MODELS_DIR)

    X_train, X_test = data["X_train"], data["X_test"]
    y_train, y_test = data["y_train"], data["y_test"]

    model_names = [
        "XGBoost",
        "Random Forest",
        "Extra Trees",
        "HistGradientBoosting",
        "Linear Regression",
    ]

    rows = []
    best = {}

    print("\n" + "=" * 80)
    print("TRAINING FIVE MODELS ON resource_demand_ml_ready.csv")
    print("=" * 80)

    for model_name in model_names:
        print(f"\n{'#' * 80}\nMODEL: {model_name}\n{'#' * 80}")
        for target in TARGETS:
            print(f"\n--- Target: {target} ---")
            est = make_model(model_name)
            yt = y_train[target].values
            ye = y_test[target].values

            t0 = time.time()
            est.fit(X_train, yt)
            train_pred = est.predict(X_train)
            test_pred = est.predict(X_test)
            elapsed = time.time() - t0

            train_r2 = float(r2_score(yt, train_pred))
            test_r2 = float(r2_score(ye, test_pred))
            mae = float(mean_absolute_error(ye, test_pred))
            rmse = float(np.sqrt(mean_squared_error(ye, test_pred)))
            mape = mape_score(ye, test_pred)
            accuracy = test_r2 * 100

            slug = MODEL_SLUGS[model_name]
            tslug = TARGET_SLUGS[target]
            model_path = MODELS_DIR / f"{tslug}_{slug}.pkl"
            joblib.dump(est, model_path)

            row = {
                "Model": model_name,
                "Target": target,
                "Train Accuracy (%)": round(train_r2 * 100, 2),
                "Test Accuracy (%)": round(accuracy, 2),
                "R2 Score": round(test_r2, 4),
                "train_r2": train_r2,
                "test_r2": test_r2,
                "accuracy_r2_pct": accuracy,
                "MAE": round(mae, 2),
                "RMSE": round(rmse, 2),
                "MAPE (%)": round(mape, 2),
                "mae": mae,
                "rmse": rmse,
                "mape": mape,
                "train_seconds": round(elapsed, 2),
                "model_file": model_path.name,
                "model": model_name,
                "target": target,
            }
            rows.append(row)

            print(
                f"Train R2 Acc: {train_r2 * 100:.2f}% | "
                f"Test R2 Acc: {accuracy:.2f}% | "
                f"MAE={mae:.2f} RMSE={rmse:.2f} MAPE={mape:.2f}% ({elapsed:.1f}s)"
            )

            prev = best.get(target)
            if prev is None or test_r2 > prev["test_r2"]:
                best[target] = {
                    "model": model_name,
                    "test_r2": test_r2,
                    "accuracy_r2_pct": accuracy,
                    "model_file": model_path.name,
                    "slug": slug,
                    "mae": mae,
                    "rmse": rmse,
                    "mape": mape,
                }

    results_df = pd.DataFrame(rows)
    results_df.to_csv(RESULTS_DIR / "model_results.csv", index=False)
    results_df.to_csv(RESULTS_DIR / "all_5_models_results.csv", index=False)

    # Comparison: Model | Food | Water | Medical | Shelter | Average (R2-based Accuracy %)
    pivot = (
        results_df.pivot(index="Model", columns="Target", values="Test Accuracy (%)")
        .reindex(columns=TARGETS)
    )
    pivot.columns = ["Food Accuracy", "Water Accuracy", "Medical Accuracy", "Shelter Accuracy"]
    pivot["Average"] = pivot.mean(axis=1)
    pivot = pivot.sort_values("Average", ascending=False)
    pivot.to_csv(RESULTS_DIR / "model_comparison.csv")
    pivot.to_csv(RESULTS_DIR / "model_average_accuracy.csv")

    best_rows = []
    for target, info in best.items():
        best_rows.append(
            {
                "Target": target,
                "Model": info["model"],
                "Test Accuracy (%)": round(info["accuracy_r2_pct"], 2),
                "R2 Score": round(info["test_r2"], 4),
                "MAE": round(info["mae"], 2),
                "RMSE": round(info["rmse"], 2),
                "MAPE (%)": round(info["mape"], 2),
            }
        )
    best_df = pd.DataFrame(best_rows)
    best_df.to_csv(RESULTS_DIR / "best_model_for_each_target.csv", index=False)

    best_payload = {
        "selected_by": "test_r2",
        "dataset": data["config"]["dataset"],
        "n_rows": data["config"]["n_rows"],
        "note": "Test Accuracy (%) is R2-based Accuracy = Test R2 x 100 (not classification accuracy).",
        "best_models": best,
        "comparison": pivot.round(4).to_dict(orient="index"),
    }
    with open(RESULTS_DIR / "best_models.json", "w", encoding="utf-8") as f:
        json.dump(best_payload, f, indent=2)

    print("\n" + "=" * 80)
    print("BEST MODEL FOR EACH TARGET (by Test R2)")
    print("=" * 80)
    for target, info in best.items():
        print(f"  {target}: {info['model']}  Test R2 Acc={info['accuracy_r2_pct']:.2f}%")

    print("\nComparison table:")
    print(pivot.round(2))
    print(f"\nSaved models -> {MODELS_DIR}")
    print(f"Saved results -> {RESULTS_DIR}")


if __name__ == "__main__":
    main()
