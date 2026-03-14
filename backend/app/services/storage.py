from urllib.parse import urljoin

import boto3
from botocore.client import Config

from app.core.config import settings


class MinioStorage:
    def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=f"http{'s' if settings.minio_secure else ''}://{settings.minio_endpoint}",
            aws_access_key_id=settings.minio_access_key,
            aws_secret_access_key=settings.minio_secret_key,
            config=Config(signature_version="s3v4"),
            region_name="us-east-1",
        )
        self.bucket = settings.minio_bucket

    def ensure_bucket(self):
        buckets = [b["Name"] for b in self.client.list_buckets().get("Buckets", [])]
        if self.bucket not in buckets:
            self.client.create_bucket(Bucket=self.bucket)

    def upload_bytes(self, key: str, content: bytes, content_type: str):
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content, ContentType=content_type)

    def object_url(self, key: str) -> str:
        base = f"http://{settings.minio_endpoint}/{self.bucket}/"
        return urljoin(base, key)
