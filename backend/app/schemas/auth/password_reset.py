from pydantic import BaseModel, Field, EmailStr
from datetime import datetime


# Запит на відновлення пароля
class PasswordResetRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "user@example.com"}
    )


class PasswordResetRequestResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={
            "example": "If this email exists in our system — password reset instructions were sent."
        }
    )


# Скидання пароля по токену
class PasswordResetConfirmRequest(BaseModel):
    token: str = Field(
        ...,
        json_schema_extra={"example": "reset-token-value"}
    )
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=72,  # важливо для bcrypt
        json_schema_extra={"example": "NewSecurePassword123"}
    )


class PasswordResetConfirmResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={
            "example": "Password has been successfully updated. All sessions invalidated."
        }
    )
    updated_at: datetime = Field(
        ...,
        json_schema_extra={"example": "2025-12-24T12:00:00"}
    )
