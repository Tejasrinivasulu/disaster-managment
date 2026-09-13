"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/")
def root():
    return {
        "message": settings.app_name,
        "docs": "/docs",
        "health": "/api/health",
        "demo_mode": settings.demo_mode,
        "ml_ready": predictor.ready,
    }
