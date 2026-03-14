from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "AI Background Remover Platform"
    env: str = "development"
    api_v1_prefix: str = "/api/v1"

    postgres_dsn: str = "postgresql+psycopg2://app:app@postgres:5432/aibg"
    redis_url: str = "redis://redis:6379/0"

    minio_endpoint: str = "minio:9000"
    minio_access_key: str = "minioadmin"
    minio_secret_key: str = "minioadmin"
    minio_bucket: str = "images"
    minio_secure: bool = False

    jwt_secret_key: str = "change-me"
    jwt_algorithm: str = "HS256"
    jwt_exp_minutes: int = 60

    captcha_secret: str = "dev-bypass"
    block_temp_domains: str = "mailinator.com,10minutemail.com,guerrillamail.com"

    verification_base_url: str = "http://localhost:8000/api/v1/auth/verify-email"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


settings = Settings()
