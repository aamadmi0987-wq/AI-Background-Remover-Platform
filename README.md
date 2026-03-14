# AI Background Remover Platform

A production-grade, asynchronous AI web application for automatic image background removal.

This project is built as a **modular distributed system** with clear service boundaries:
- React frontend (user interface)
- NGINX reverse proxy (edge routing)
- FastAPI backend (auth, APIs, orchestration)
- Redis queue (async job buffering)
- Worker service (AI processing via `rembg`)
- MinIO object storage (input/output image persistence)
- PostgreSQL (relational persistence)

---

## Table of Contents
1. [Platform Features](#platform-features)
2. [High-Level Architecture](#high-level-architecture)
3. [Detailed Processing Flow](#detailed-processing-flow)
4. [Project Directory Structure](#project-directory-structure)
5. [Backend Service Design](#backend-service-design)
6. [Worker Service Design](#worker-service-design)
7. [Data Model](#data-model)
8. [API Surface](#api-surface)
9. [Security Model](#security-model)
10. [Health Checks and Readiness](#health-checks-and-readiness)
11. [Local Development](#local-development)
12. [Environment Variables](#environment-variables)
13. [Production Hardening Recommendations](#production-hardening-recommendations)
14. [Troubleshooting](#troubleshooting)

---

## Platform Features

### User-facing capabilities
- Email/password signup
- Email verification before login
- JWT-authenticated sessions
- Image upload endpoint
- Asynchronous background-removal jobs
- Job status polling
- User image history
- Download-ready output URLs
- Frontend now includes login/signup UI, token persistence, job polling, and upload history panel

### Platform capabilities
- Non-blocking API via Redis-backed worker queue
- Worker dependency includes `onnxruntime` required by `rembg` execution in containers.
- Separation of API and heavy AI execution
- S3-compatible storage via MinIO
- Dependency-aware readiness endpoint
- Containerized deployment with Docker Compose

---

## High-Level Architecture

```text
┌─────────────────────┐
│   React Frontend    │
│  (Tailwind + Vite)  │
└──────────┬──────────┘
           │ HTTP
           ▼
┌─────────────────────┐
│   NGINX Proxy       │
│ - /      -> frontend│
│ - /api/* -> backend │
└──────────┬──────────┘
           │
           ▼
┌───────────────────────────────────────────┐
│            FastAPI Backend                │
│ Auth | Upload | Job Create | Job Status   │
│ Image History | Health /ready             │
└──────┬───────────────────────────────┬────┘
       │                               │
       │ enqueue job                   │ DB writes/reads
       ▼                               ▼
┌───────────────┐                 ┌───────────────┐
│     Redis     │                 │  PostgreSQL   │
│  Job Queue    │                 │ users/jobs/...│
└───────┬───────┘                 └───────────────┘
        │
        │ consume
        ▼
┌───────────────────────────────────────────┐
│            Worker Service                  │
│ Redis BLPOP -> rembg -> MinIO upload      │
│ update job status in PostgreSQL            │
└──────────────────────────┬────────────────┘
                           ▼
                    ┌───────────────┐
                    │    MinIO      │
                    │ input/output  │
                    │ image objects │
                    └───────────────┘
```

### Request path summary
- **UI/API traffic:** Browser → NGINX → FastAPI
- **Heavy compute path:** FastAPI → Redis queue → Worker → MinIO/PostgreSQL

---

## Detailed Processing Flow

### 1) Signup and verification
1. Client sends `POST /api/v1/auth/signup`.
2. Backend validates CAPTCHA token, blocks temporary domains, hashes password, creates user.
3. Backend returns a verification URL containing a short-lived JWT token.
4. Client submits token to `POST /api/v1/auth/verify-email`.
5. Backend marks `email_verified = true`.

### 2) Authenticated login
1. Client sends `POST /api/v1/auth/login` with email/password.
2. Backend validates credentials and verification status.
3. Backend returns JWT access token.

### 3) Upload and async background removal
1. Client uploads image to `POST /api/v1/images/upload`.
2. Backend stores file in MinIO and writes image metadata in PostgreSQL.
3. Client requests background removal via `POST /api/v1/jobs/remove-background`.
4. Backend creates `jobs` row (`queued`) and pushes payload to Redis.
5. Worker consumes queue message, marks job `processing`.
6. Worker downloads input image, removes background via `rembg`.
7. Worker uploads output image to MinIO.
8. Worker updates job row: `completed` + `output_image_url`.
9. Client polls `GET /api/v1/jobs/{job_id}` until completion.

---

## Project Directory Structure

```text
.
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── deps.py
│   │   │   └── routes/
│   │   │       ├── auth.py
│   │   │       ├── images.py
│   │   │       ├── jobs.py
│   │   │       └── health.py
│   │   ├── core/
│   │   │   └── config.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   └── session.py
│   │   ├── models/
│   │   │   ├── user.py
│   │   │   ├── job.py
│   │   │   └── image.py
│   │   ├── schemas/
│   │   └── services/
│   │       ├── security.py
│   │       ├── storage.py
│   │       ├── queue.py
│   │       └── captcha.py
│   ├── Dockerfile
│   └── requirements.txt
├── worker/
│   ├── worker.py
│   ├── models.py
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   ├── components/
│   │   ├── pages/
│   │   └── styles/
│   ├── Dockerfile
│   └── package.json
├── nginx/
│   └── nginx.conf
├── docs/
│   └── api-examples.md
├── docker-compose.yml
└── .env.example
```

---

## Backend Service Design

### Core responsibilities
- Authentication and authorization
- Upload orchestration
- Job lifecycle creation
- User history retrieval
- Health and readiness checks

### Internal layering
- **routes/**: HTTP handlers and response contracts
- **schemas/**: request/response validation
- **models/**: SQLAlchemy persistence models
- **services/**: reusable logic (JWT, queue, storage, CAPTCHA)
- **db/**: connection/session management
- **core/**: config and global settings

### Why this scales
- API remains responsive because expensive inference is offloaded.
- Stateless API workers can be horizontally scaled behind NGINX.
- Queue depth naturally buffers bursts.

---

## Worker Service Design

### Responsibilities
- Block on Redis queue (`BLPOP`)
- Update job state transitions (`queued -> processing -> completed/failed`)
- Run AI background removal with `rembg`
- Upload processed output to MinIO
- Persist status and output URL back to PostgreSQL

### Scale strategy
- Increase worker replicas to improve throughput.
- Keep queue semantics simple and observable.
- Move toward dead-letter queue + retries for fault tolerance (recommended next step).

---

## Data Model

### `users`
- `id`
- `email` (unique)
- `password_hash`
- `email_verified`
- `created_at`
- `plan`

### `jobs`
- `id`
- `user_id` (FK)
- `status`
- `input_image_url`
- `output_image_url`
- `created_at`

### `images`
- `id`
- `user_id` (FK)
- `image_url`
- `created_at`

---

## API Surface

### Authentication
- `POST /api/v1/auth/signup`
- `POST /api/v1/auth/login`
- `POST /api/v1/auth/verify-email`

### Image & job APIs
- `POST /api/v1/images/upload`
- `POST /api/v1/jobs/remove-background`
- `GET /api/v1/jobs/{job_id}`
- `GET /api/v1/images/history`

### Health
- `GET /health`
- `GET /health/live`
- `GET /health/ready`

For concrete payload examples, see [`docs/api-examples.md`](docs/api-examples.md).

---

## Security Model

- Password hashing via bcrypt (`passlib` context)
- JWT bearer tokens for API access
- Email verification gate before login
- Temporary-domain blocklist at signup
- CAPTCHA validation hook (dev bypass available)
- MIME-type guard for uploads (`image/*`)

> Important: replace development secrets and bypass settings before production deployment.

---

## Health Checks and Readiness

### Liveness (`/health/live`)
- Confirms process is running.

### Readiness (`/health/ready`)
- Verifies live connectivity to:
  - PostgreSQL (`SELECT 1`)
  - Redis (`PING`)
  - MinIO (`list_buckets`)

Use readiness for orchestrator traffic gating.

---

## Local Development

### Prerequisites
- Docker + Docker Compose
- (Optional) Node/Python if running services outside containers

### Quick start
```bash
cp .env.example .env
docker compose up --build
```

### Service endpoints (default)
- App entrypoint via NGINX: `http://localhost`
- Backend via NGINX API route: `http://localhost/api/v1/...`
- MinIO API: `http://localhost:9000` (if port is exposed in your compose override)
- MinIO Console: `http://localhost:9001` (if exposed)

---

## Environment Variables

Defined in `.env.example`:

- **App:** `APP_NAME`, `ENV`, `API_V1_PREFIX`
- **PostgreSQL:** `POSTGRES_DSN`
- **Redis:** `REDIS_URL`
- **MinIO:** `MINIO_ENDPOINT`, `MINIO_ACCESS_KEY`, `MINIO_SECRET_KEY`, `MINIO_BUCKET`, `MINIO_SECURE`
- **JWT:** `JWT_SECRET_KEY`, `JWT_ALGORITHM`, `JWT_EXP_MINUTES`
- **Auth controls:** `CAPTCHA_SECRET`, `BLOCK_TEMP_DOMAINS`, `VERIFICATION_BASE_URL`

---

## Production Hardening Recommendations

1. **Migrations**
   - Introduce Alembic migration flow (avoid runtime `create_all` for production).

2. **Email verification delivery**
   - Replace returned verification URL with real provider integration (SES/SendGrid/Postmark).

3. **Queue reliability**
   - Add retry policy, dead-letter queue, visibility timeout strategy, idempotency keys.

4. **Storage security**
   - Use private bucket policies + pre-signed URLs instead of public object paths.

5. **Authentication hardening**
   - Add refresh tokens, rotation, revocation list, and stricter token lifetimes.

6. **Abuse protection**
   - API rate limiting, WAF rules, IP throttling, upload size limits.

7. **Observability**
   - Structured logs, OpenTelemetry traces, Prometheus metrics, alerting.

8. **Kubernetes readiness**
   - Convert compose to Helm/Kustomize for multi-replica deployment patterns.

---

## Troubleshooting

### Worker not processing jobs
- Verify Redis is reachable from worker.
- Confirm queue name matches (`bg_removal_jobs`).
- Check worker logs for `rembg`/dependency errors.
- If you see `ModuleNotFoundError: onnxruntime`, rebuild the worker image after pulling latest code.

### Readiness endpoint failing
- Inspect `/health/ready` response object to identify failed dependency.
- Confirm DSNs, credentials, and container network DNS names.

### Upload succeeds but output missing
- Confirm worker has MinIO write access.
- Check job status (`failed` vs `completed`) and worker exception logs.

---

## License

Use and adapt this scaffold for your own projects. Add a dedicated license file for public distribution.
