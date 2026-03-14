# AI Background Remover Platform

Production-oriented scaffold for an asynchronous AI image background removal platform.

## Services
- **Frontend (React + Tailwind)**
- **Backend API (FastAPI)**
- **Worker (Redis queue consumer + rembg)**
- **Redis**
- **PostgreSQL**
- **MinIO**
- **NGINX reverse proxy**

## Quick start
```bash
cp .env.example .env
docker compose up --build
```

## API endpoints
### Authentication
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-email`

### Image processing
- `POST /api/v1/images/upload`
- `POST /api/v1/jobs/remove-background`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/images/history`

### Health
- `GET /health`
- `GET /health/live`
- `GET /health/ready`

## Notes
- Signup blocks temporary email domains.
- CAPTCHA check supports a dev bypass (`captcha_token=dev-pass` when `CAPTCHA_SECRET=dev-bypass`).
- Worker consumes queue `bg_removal_jobs`.
