import io
import json
import logging
import os
import uuid

import boto3
import redis
import requests
from botocore.client import Config
from rembg import remove
from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from models import Job

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("worker")

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")
QUEUE_NAME = os.getenv("QUEUE_NAME", "bg_removal_jobs")
POSTGRES_DSN = os.getenv("POSTGRES_DSN", "postgresql+psycopg2://app:app@postgres:5432/aibg")
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "minio:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "images")


def get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url=f"http://{MINIO_ENDPOINT}",
        aws_access_key_id=MINIO_ACCESS_KEY,
        aws_secret_access_key=MINIO_SECRET_KEY,
        config=Config(signature_version="s3v4"),
        region_name="us-east-1",
    )


def ensure_bucket(client):
    buckets = [b["Name"] for b in client.list_buckets().get("Buckets", [])]
    if MINIO_BUCKET not in buckets:
        client.create_bucket(Bucket=MINIO_BUCKET)


def process_job(payload: dict, db: Session, s3_client):
    job = db.query(Job).filter(Job.id == payload["job_id"]).first()
    if not job:
        logger.warning("Job %s not found", payload["job_id"])
        return

    job.status = "processing"
    db.commit()

    try:
        image_bytes = requests.get(job.input_image_url, timeout=30).content
        output = remove(image_bytes)

        key = f"processed/{job.user_id}/{uuid.uuid4().hex}.png"
        s3_client.put_object(Bucket=MINIO_BUCKET, Key=key, Body=io.BytesIO(output).getvalue(), ContentType="image/png")

        output_url = f"http://{MINIO_ENDPOINT}/{MINIO_BUCKET}/{key}"
        job.output_image_url = output_url
        job.status = "completed"
    except Exception as exc:
        logger.exception("Failed processing job %s", job.id)
        job.status = "failed"
        job.output_image_url = None
        raise exc
    finally:
        db.commit()


def run_worker():
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    engine = create_engine(POSTGRES_DSN, pool_pre_ping=True)
    s3_client = get_s3_client()
    ensure_bucket(s3_client)

    logger.info("Worker started; listening queue=%s", QUEUE_NAME)

    while True:
        _, message = redis_client.blpop(QUEUE_NAME)
        payload = json.loads(message)
        with Session(engine) as db:
            try:
                process_job(payload, db, s3_client)
            except Exception:
                continue


if __name__ == "__main__":
    run_worker()
