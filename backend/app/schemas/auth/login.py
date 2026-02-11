from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


class LoginRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "user@example.com"}
    )
    password: str = Field(
        ...,
        min_length=6,
        json_schema_extra={"example": "StrongPassword123"}
    )


class LoginResponse(BaseModel):
    session_token: str = Field(
        ...,
        json_schema_extra={"example": "jwt-token-here"}
    )
    expires_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-12-24T12:00:00"}
    )
