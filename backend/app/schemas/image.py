from datetime import datetime

from pydantic import BaseModel


class UploadResponse(BaseModel):
    image_url: str


class JobCreateResponse(BaseModel):
    job_id: int
    status: str


class JobResponse(BaseModel):
    id: int
    status: str
    input_image_url: str
    output_image_url: str | None
    created_at: datetime


class ImageHistoryItem(BaseModel):
    id: int
    image_url: str
    created_at: datetime
