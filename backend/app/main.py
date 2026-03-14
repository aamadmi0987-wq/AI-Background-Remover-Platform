import logging

from fastapi import FastAPI

from app.api.routes import auth, health, images, jobs
from app.core.config import settings
from app.db.session import engine
from app.models.base import Base

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")

app = FastAPI(title=settings.app_name)

Base.metadata.create_all(bind=engine)

app.include_router(auth.router, prefix=settings.api_v1_prefix)
app.include_router(images.router, prefix=settings.api_v1_prefix)
app.include_router(jobs.router, prefix=settings.api_v1_prefix)
app.include_router(health.router)
