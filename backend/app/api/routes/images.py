import uuid

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.db.session import get_db
from app.models.image import Image
from app.models.job import Job
from app.models.user import User
from app.schemas.image import ImageHistoryItem, JobCreateResponse, UploadResponse
from app.services.queue import JobQueue
from app.services.storage import MinioStorage

router = APIRouter(tags=["images"])


@router.post("/images/upload", response_model=UploadResponse)
async def upload_image(
    file: UploadFile = File(...),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are allowed")

    storage = MinioStorage()
    storage.ensure_bucket()

    extension = file.filename.split(".")[-1] if file.filename and "." in file.filename else "png"
    key = f"uploads/{user.id}/{uuid.uuid4().hex}.{extension}"
    content = await file.read()
    storage.upload_bytes(key, content, file.content_type)
    image_url = storage.object_url(key)

    image = Image(user_id=user.id, image_url=image_url)
    db.add(image)
    db.commit()

    return UploadResponse(image_url=image_url)


@router.post("/jobs/remove-background", response_model=JobCreateResponse)
def remove_background(
    image_url: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = Job(user_id=user.id, status="queued", input_image_url=image_url)
    db.add(job)
    db.commit()
    db.refresh(job)

    JobQueue().enqueue({"job_id": job.id, "user_id": user.id, "input_image_url": image_url})
    return JobCreateResponse(job_id=job.id, status=job.status)


@router.get("/images/history", response_model=list[ImageHistoryItem])
def history(user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.query(Image).filter(Image.user_id == user.id).order_by(Image.created_at.desc()).all()
    return [ImageHistoryItem(id=r.id, image_url=r.image_url, created_at=r.created_at) for r in rows]
