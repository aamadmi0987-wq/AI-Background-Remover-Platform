# Example API Requests and Responses

## Signup
```http
POST /api/v1/auth/signup
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPassword123!",
  "captcha_token": "dev-pass"
}
```

```json
{
  "message": "Signup successful. Verify email before login.",
  "verification_url": "http://localhost/api/v1/auth/verify-email?token=..."
}
```

## Verify email
```http
POST /api/v1/auth/verify-email
Content-Type: application/json

{
  "token": "<verification_token>"
}
```

## Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "StrongPassword123!"
}
```

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer"
}
```

## Upload image
```http
POST /api/v1/images/upload
Authorization: Bearer <jwt>
Content-Type: multipart/form-data
```

```json
{
  "image_url": "http://minio:9000/images/uploads/1/abc123.png"
}
```

## Create remove background job
```http
POST /api/v1/jobs/remove-background?image_url=http://minio:9000/images/uploads/1/abc123.png
Authorization: Bearer <jwt>
```

```json
{
  "job_id": 42,
  "status": "queued"
}
```

## Get job
```http
GET /api/v1/jobs/42
Authorization: Bearer <jwt>
```

```json
{
  "id": 42,
  "status": "completed",
  "input_image_url": "http://minio:9000/images/uploads/1/abc123.png",
  "output_image_url": "http://minio:9000/images/processed/1/xyz999.png",
  "created_at": "2026-01-01T10:00:00"
}
```
