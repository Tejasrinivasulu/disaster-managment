"""Vercel serverless entrypoint for the FastAPI backend."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BACKEND = ROOT / "backend"
ML = ROOT / "ml"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ML) not in sys.path:
    sys.path.insert(0, str(ML))

# Vercel sets VERCEL=1. Use writable /tmp for SQLite on serverless.
if os.environ.get("VERCEL"):
    os.environ.setdefault("APP_ENV", "production")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/disaster_response.db")
    os.environ.setdefault(
        "SECRET_KEY",
        os.environ.get("SECRET_KEY", "vercel-demo-secret-change-me"),
    )
    # Same-origin SPA + API — include localhost for local `vercel dev`
    os.environ.setdefault(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    )
    os.environ["ML_MODELS_DIR"] = str(ML / "models")
    os.environ["ML_RESULTS_DIR"] = str(ML / "results")

from app import config as app_config  # noqa: E402

app_config.get_settings.cache_clear()

from app.main import app  # noqa: E402, F401
