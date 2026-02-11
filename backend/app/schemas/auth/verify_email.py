from pydantic import BaseModel, Field


class EmailVerificationRequest(BaseModel):
    token: str = Field(
        ...,
        json_schema_extra={"example": "secureverificationtoken123"}
    )


class EmailVerificationResponse(BaseModel):
    message: str = Field(
        ...,
        json_schema_extra={"example": "Email successfully confirmed."}
    )
