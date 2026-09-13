"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.config import get_settings
from app.database import SessionLocal, init_db
from app.ml.predictor import predictor
from app.routes import (
    admin,
    auth,
    dashboard,
    disasters,
    field_reports,
    health,
    optimization,
    predict,
    reports,
    resources,
    routes,
    teams,
)
from app.services.seed import seed_database

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)
settings = get_settings()


def frontend_dist() -> Path:
    """Repo root / frontend / dist (works when cwd is backend/)."""
    return Path(__file__).resolve().parents[2] / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting %s (demo_mode=%s)", settings.app_name, settings.demo_mode)
    init_db()
    db = SessionLocal()
    try:
        seed_database(db)
    finally:
        db.close()
    predictor.load()
    if predictor.ready:
        logger.info("ML demand models ready")
    else:
        logger.warning("ML models not ready: %s", predictor.error)
    yield
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.app_name,
    description="AI-Based Disaster Response Management System for Resource Allocation and Relief Coordination",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_origin_regex=settings.cors_origin_regex or None,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(disasters.router, prefix="/api")
app.include_router(disasters.zones_router, prefix="/api")
app.include_router(resources.router, prefix="/api")
app.include_router(predict.router, prefix="/api")
app.include_router(optimization.router, prefix="/api")
app.include_router(routes.router, prefix="/api")
app.include_router(teams.teams_router, prefix="/api")
app.include_router(teams.missions_router, prefix="/api")
app.include_router(field_reports.router, prefix="/api")
app.include_router(reports.scenarios_router, prefix="/api")
app.include_router(reports.reports_router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api")
def api_info():
    return {
        "status": "ok",
        "health": "/api/health",
        "docs": "/docs",
        "message": settings.app_name,
    }


@app.get("/")
async def root():
    index = frontend_dist() / "index.html"
    if index.exists():
        return FileResponse(index)
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
        "demo_mode": settings.demo_mode,
        "ml_ready": predictor.ready,
    }


_dist = frontend_dist()
if (_dist / "index.html").exists():
    _assets = _dist / "assets"
    if _assets.exists():
        app.mount("/assets", StaticFiles(directory=str(_assets)), name="assets")

    @app.get("/{full_path:path}", include_in_schema=False)
    async def spa_fallback(full_path: str):
        if (
            full_path == "api"
            or full_path.startswith("api/")
            or full_path in {"docs", "redoc", "openapi.json"}
            or full_path.startswith("docs/")
        ):
            raise HTTPException(status_code=404, detail="Not Found")
        candidate = frontend_dist() / full_path
        if candidate.is_file():
            return FileResponse(candidate)
        return FileResponse(frontend_dist() / "index.html")
