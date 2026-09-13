# ML Report

## Problem type

Multi-target **regression** for continuous relief demand:

- food_demand
- water_demand_litres
- medical_kit_demand
- shelter_demand

## Models compared

1. XGBoost Regressor
2. Random Forest Regressor
3. Extra Trees Regressor
4. HistGradientBoosting Regressor
5. Linear Regression

## Metrics

- Train R² / Test R²
- **R²-based Accuracy (%) = Test R² × 100**
- MAE, RMSE, MAPE

Do not interpret R²-based Accuracy as classification accuracy.

## Selection rule

Best model per target = highest **Test R²** (saved to `ml/results/best_models.json`).

## Artifacts

- `ml/models/*.pkl` — trained estimators + `preprocessor.pkl`
- `ml/results/model_results.csv`
- `ml/results/model_comparison.csv`
- `ml/results/best_models.json`

Re-run training after replacing the dataset CSV:

```powershell
cd ml
python train_models.py
```
