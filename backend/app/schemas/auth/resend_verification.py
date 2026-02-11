from pydantic import BaseModel, Field, EmailStr


class ResendVerificationRequest(BaseModel):
    email: EmailStr = Field(
        ...,
        json_schema_extra={"example": "user@example.com"}
    )


class ResendVerificationResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={"example": "Verification email has been sent."}
    )
