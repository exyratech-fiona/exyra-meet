from pydantic_settings import BaseSettings
from typing import List
import os


class Settings(BaseSettings):
    # App
    APP_NAME: str = "Exyra Technologies"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    SECRET_KEY: str = "change-me-in-production-use-openssl-rand-hex-32"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours

    # Database (MySQL)
    DATABASE_URL: str = "mysql+aiomysql://exyra:exyra_pass_2024@127.0.0.1:3306/exyra_meet"
    DATABASE_URL_SYNC: str = "mysql+pymysql://exyra:exyra_pass_2024@127.0.0.1:3306/exyra_meet"

    # Google OAuth
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"

    # Google Calendar / Meet
    GOOGLE_SERVICE_ACCOUNT_FILE: str = "credentials/service_account.json"
    GOOGLE_CALENDAR_ID: str = "primary"

    # Gmail / SMTP
    GMAIL_SENDER_EMAIL: str = ""
    GMAIL_SENDER_NAME: str = "Exyra Technologies"
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""

    # WhatsApp Cloud API
    WHATSAPP_API_URL: str = "https://graph.facebook.com/v19.0"
    WHATSAPP_PHONE_NUMBER_ID: str = ""
    WHATSAPP_ACCESS_TOKEN: str = ""
    WHATSAPP_VERIFY_TOKEN: str = "exyra_verify_token"

    # CORS
    ALLOWED_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://exyra.tech",
    ]

    # Timezone
    DEFAULT_TIMEZONE: str = "Asia/Kolkata"

    # Frontend URL
    FRONTEND_URL: str = "http://localhost:3000"

    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
