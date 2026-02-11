# app/schemas/auth/register.py
from pydantic import BaseModel, Field, EmailStr, field_validator, ConfigDict
from datetime import date


class RegisterRequest(BaseModel):
    user_name: str = Field(...)
    email: EmailStr = Field(...)
    password: str = Field(..., min_length=8)
    date_of_birth: date = Field(...)

    @field_validator('date_of_birth')
    @classmethod
    def validate_age(cls, v):
        return v


class RegisterResponse(BaseModel):
    id: int
    user_name: str
    email: str
    date_of_birth: date

    model_config = ConfigDict(from_attributes=True)