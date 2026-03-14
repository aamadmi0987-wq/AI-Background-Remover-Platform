from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import LoginRequest, SignupRequest, TokenResponse, VerifyEmailRequest
from app.services.captcha import verify_captcha
from app.services.security import create_access_token, decode_token, hash_password, verify_password

router = APIRouter(prefix="/auth", tags=["auth"])


def _is_blocked_domain(email: str) -> bool:
    blocked = {d.strip().lower() for d in settings.block_temp_domains.split(",") if d.strip()}
    domain = email.split("@")[-1].lower()
    return domain in blocked


@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(payload: SignupRequest, db: Session = Depends(get_db)):
    if _is_blocked_domain(payload.email):
        raise HTTPException(status_code=400, detail="Temporary email domains are not allowed")
    if not verify_captcha(payload.captcha_token, settings.captcha_secret):
        raise HTTPException(status_code=400, detail="Invalid captcha")
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(status_code=409, detail="Email already registered")

    user = User(email=payload.email, password_hash=hash_password(payload.password), email_verified=False)
    db.add(user)
    db.commit()

    verification_token = create_access_token(payload.email, minutes=30)
    verification_url = f"{settings.verification_base_url}?token={verification_token}"
    return {"message": "Signup successful. Verify email before login.", "verification_url": verification_url}


@router.post("/verify-email")
def verify_email(payload: VerifyEmailRequest, db: Session = Depends(get_db)):
    decoded = decode_token(payload.token)
    if not decoded or "sub" not in decoded:
        raise HTTPException(status_code=400, detail="Invalid verification token")

    user = db.query(User).filter(User.email == decoded["sub"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email_verified = True
    db.commit()
    return {"message": "Email verified"}


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if not user.email_verified:
        raise HTTPException(status_code=403, detail="Email not verified")

    token = create_access_token(user.email)
    return TokenResponse(access_token=token)
