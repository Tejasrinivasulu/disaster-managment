"""Vercel FastAPI entrypoint — serves /api/* and the React SPA."""

from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
ML = ROOT / "ml"
DIST = ROOT / "frontend" / "dist"

if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))
if str(ML) not in sys.path:
    sys.path.insert(0, str(ML))

if os.environ.get("VERCEL"):
    os.environ.setdefault("APP_ENV", "production")
    os.environ.setdefault("DEBUG", "false")
    os.environ.setdefault("DEMO_MODE", "true")
    os.environ.setdefault("DATABASE_URL", "sqlite:////tmp/disaster_response.db")
    os.environ.setdefault(
        "SECRET_KEY",
        os.environ.get("SECRET_KEY", "vercel-demo-secret-change-me"),
    )
    os.environ.setdefault(
        "CORS_ORIGINS",
        "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000",
    )
    os.environ["ML_MODELS_DIR"] = str(ML / "models")
    os.environ["ML_RESULTS_DIR"] = str(ML / "results")

from app import config as app_config  # noqa: E402

app_config.get_settings.cache_clear()

from app.main import app  # noqa: E402
from fastapi import HTTPException  # noqa: E402
from fastapi.responses import FileResponse  # noqa: E402
from fastapi.staticfiles import StaticFiles  # noqa: E402

# Vite production build: serve UI for non-API paths (registered last).
if DIST.exists() and (DIST / "index.html").exists():
    assets_dir = DIST / "assets"
    if assets_dir.exists():
        app.mount("/assets", StaticFiles(directory=str(assets_dir)), name="assets")

    async def _spa_index():
        return FileResponse(DIST / "index.html")

    # Replace JSON root with SPA when a build is present
    app.router.routes = [
        r
        for r in app.router.routes
        if not (
            getattr(r, "path", None) == "/"
            and getattr(r, "methods", None) == {"GET"}
            and getattr(r, "name", "") == "root"
        )
    ]
    app.add_api_route("/", _spa_index, methods=["GET"], include_in_schema=False)

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if (
            full_path == "api"
            or full_path.startswith("api/")
            or full_path in {"docs", "redoc", "openapi.json"}
            or full_path.startswith("docs/")
        ):
            raise HTTPException(status_code=404, detail="Not Found")

        candidate = DIST / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(DIST / "index.html")
