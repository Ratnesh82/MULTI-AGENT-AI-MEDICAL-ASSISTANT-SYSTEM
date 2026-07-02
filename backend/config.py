"""
FCMAS-W Configuration
Loads settings from environment variables via .env file.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    mongo_uri: str = "mongodb://localhost:27017"
    db_name: str = "fcmas_db"

    # Auth
    secret_key: str = "dev-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 1440

    # Email / SMTP (optional)
    smtp_host: str = ""
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@fcmas-w.health"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
