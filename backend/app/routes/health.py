"""Health check and system status routes."""

from datetime import datetime, timezone

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter(tags=["Health"])


@router.get("/health")
def health_check():
    settings = get_settings()
    return {
        "status": "ok",
        "service": settings.app_name,
        "environment": settings.app_env,
        "demo_mode": settings.demo_mode,
        "external_apis": settings.external_apis_configured,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
