"""Generate a synthetic disaster demand dataset for local training/demo.

If you have a real CSV (~212k rows), place it at:
  ml/data/disaster_demand_dataset.csv

Expected target columns (never used as features):
  food_demand, water_demand_litres, medical_kit_demand, shelter_demand
"""

from pathlib import Path

import numpy as np
import pandas as pd

DATA_DIR = Path(__file__).resolve().parent
OUTPUT = DATA_DIR / "disaster_demand_dataset.csv"

TARGETS = [
    "food_demand",
    "water_demand_litres",
    "medical_kit_demand",
    "shelter_demand",
]


def generate(n_rows: int = 8000, seed: int = 42) -> pd.DataFrame:
    rng = np.random.default_rng(seed)

    disaster_types = np.array(["Flood", "Earthquake", "Cyclone", "Landslide", "Drought"])
    subtypes = np.array(["Riverine", "Flash", "Moderate", "Severe", "Coastal", "Urban"])

    years = rng.integers(2015, 2025, n_rows)
    months = rng.integers(1, 13, n_rows)
    days = rng.integers(1, 28, n_rows)
    event_date = pd.to_datetime(
        dict(year=years, month=months, day=days),
        errors="coerce",
    )

    population = rng.integers(2000, 200000, n_rows)
    population_density = rng.uniform(50, 5000, n_rows)
    vulnerability_score = rng.uniform(0.1, 0.95, n_rows)
    severity_score = rng.uniform(0.1, 0.99, n_rows)
    building_damage_pct = rng.uniform(0, 90, n_rows)
    road_damage_pct = rng.uniform(0, 80, n_rows)
    rainfall = rng.uniform(0, 400, n_rows)
    humidity = rng.uniform(20, 99, n_rows)
    elderly_pct = rng.uniform(0.05, 0.25, n_rows)
    children_pct = rng.uniform(0.1, 0.35, n_rows)
    medical_dependency_pct = rng.uniform(0.02, 0.2, n_rows)
    accessibility_score = rng.uniform(0.2, 1.0, n_rows)
    latitude = rng.uniform(8.0, 35.0, n_rows)
    longitude = rng.uniform(68.0, 97.0, n_rows)

    # Continuous demand targets with realistic relationships + noise
    food_demand = (
        population * (0.15 + 0.4 * severity_score)
        * (1 + 0.35 * vulnerability_score)
        * (1 + building_damage_pct / 200)
        + rng.normal(0, 500, n_rows)
    )
    water_demand_litres = (
        population * (8 + 20 * severity_score)
        * (1 + 0.25 * vulnerability_score)
        * (1 + rainfall / 500)
        + rng.normal(0, 2000, n_rows)
    )
    medical_kit_demand = (
        population * (0.01 + 0.05 * severity_score)
        * (1 + medical_dependency_pct * 3)
        * (1 + building_damage_pct / 150)
        + rng.normal(0, 50, n_rows)
    )
    shelter_demand = (
        population * (0.05 + 0.25 * severity_score)
        * (1 + building_damage_pct / 100)
        * (1 + elderly_pct + children_pct)
        * (1 + (1 - accessibility_score) * 0.3)
        + rng.normal(0, 200, n_rows)
    )

    df = pd.DataFrame(
        {
            "event_date": event_date,
            "disaster_type": rng.choice(disaster_types, n_rows),
            "subtype": rng.choice(subtypes, n_rows),
            "latitude": latitude,
            "longitude": longitude,
            "population": population,
            "population_density": population_density,
            "vulnerability_score": vulnerability_score,
            "severity_score": severity_score,
            "building_damage_pct": building_damage_pct,
            "road_damage_pct": road_damage_pct,
            "rainfall": rainfall,
            "humidity": humidity,
            "elderly_pct": elderly_pct,
            "children_pct": children_pct,
            "medical_dependency_pct": medical_dependency_pct,
            "accessibility_score": accessibility_score,
            "food_demand": np.clip(food_demand, 0, None),
            "water_demand_litres": np.clip(water_demand_litres, 0, None),
            "medical_kit_demand": np.clip(medical_kit_demand, 0, None),
            "shelter_demand": np.clip(shelter_demand, 0, None),
        }
    )

    # Inject some missing values to exercise preprocessing
    for col in ["rainfall", "humidity", "population_density", "subtype"]:
        mask = rng.random(n_rows) < 0.02
        df.loc[mask, col] = np.nan

    return df


def main():
    if OUTPUT.exists():
        print(f"Dataset already exists: {OUTPUT} ({OUTPUT.stat().st_size} bytes)")
        print("Delete it first if you want to regenerate.")
        return
    df = generate()
    df.to_csv(OUTPUT, index=False)
    print(f"Wrote {len(df):,} rows to {OUTPUT}")
    print("Targets:", TARGETS)
    print(df[TARGETS].describe().round(2))


if __name__ == "__main__":
    main()
