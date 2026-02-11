from datetime import timedelta
from pydantic_settings import BaseSettings
from pydantic import EmailStr

import os
from dotenv import load_dotenv

# Тривалість життя токена підтвердження email
EMAIL_VERIFICATION_TOKEN_LIFETIME = timedelta(minutes=15)

load_dotenv()

# Тривалість життя токена підтвердження email
EMAIL_VERIFICATION_TOKEN_LIFETIME = timedelta(minutes=15)

PASSWORD_RESET_TOKEN_LIFETIME = timedelta(hours=1)

# JWT settings
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRES_DELTA = timedelta(seconds=int(os.getenv("JWT_EXPIRES_DELTA", 3600)))  # 1 година за замовчуванням

class Settings(BaseSettings):
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_EMAIL: EmailStr
    SMTP_PASSWORD: str
    SMTP_FROM_NAME: str
    FRONTEND_BASE_URL: str

    EMAIL_VERIFICATION_TOKEN_LIFETIME: int = 900
    PASSWORD_RESET_TOKEN_LIFETIME: int = 3600

settings = Settings()
