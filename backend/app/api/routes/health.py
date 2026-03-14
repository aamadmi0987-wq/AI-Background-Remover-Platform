from fastapi import APIRouter
from sqlalchemy import text

from app.core.config import settings
from app.db.session import SessionLocal
from app.services.storage import MinioStorage
import redis

router = APIRouter(prefix="/health", tags=["health"])


@router.get("")
def health():
    return {"status": "ok", "service": settings.app_name}


@router.get("/live")
def liveness():
    return {"status": "alive"}


@router.get("/ready")
def readiness():
    checks = {"postgres": False, "redis": False, "minio": False}

    db = SessionLocal()
    try:
        db.execute(text("SELECT 1"))
        checks["postgres"] = True
    finally:
        db.close()

    redis.Redis.from_url(settings.redis_url).ping()
    checks["redis"] = True

    MinioStorage().client.list_buckets()
    checks["minio"] = True

    overall = all(checks.values())
    return {"status": "ready" if overall else "not_ready", "checks": checks}
