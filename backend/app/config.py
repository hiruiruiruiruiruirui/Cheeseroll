"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # App
    APP_ENV: str = "development"
    SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 43200  # 30 days

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/study_assistant"

    @property
    def db_url_with_ssl(self):
        url = self.DATABASE_URL
        if "?ssl=" not in url:
            return url + "?ssl=require"
        return url

    # Tencent COS
    COS_SECRET_ID: str = ""
    COS_SECRET_KEY: str = ""
    COS_REGION: str = "ap-guangzhou"
    COS_BUCKET: str = ""

    # Anthropic Claude
    ANTHROPIC_API_KEY: str = ""

    # WeChat
    WECHAT_APPID: str = ""
    WECHAT_SECRET: str = ""
    WECHAT_MCH_ID: str = ""
    WECHAT_PAY_API_KEY: str = ""
    WECHAT_PAY_SERIAL_NO: str = ""
    WECHAT_PAY_PRIVATE_KEY_PATH: str = ""

    # Lemon Squeezy
    LEMON_SQUEEZY_API_KEY: str = ""
    LEMON_SQUEEZY_STORE_ID: str = ""
    LEMON_SQUEEZY_WEBHOOK_SECRET: str = ""
    FRONTEND_URL: str = "http://localhost:5173"

    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"

    # Rate Limit
    RATE_LIMIT_PER_DAY: int = 10

    # File Upload
    MAX_UPLOAD_SIZE_MB: int = 50
    ALLOWED_EXTENSIONS: list[str] = ["pptx", "docx", "pdf"]

    # COS temp file lifetime
    FILE_EXPIRE_HOURS: int = 24

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
