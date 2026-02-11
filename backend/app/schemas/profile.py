from datetime import date
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileResponse(BaseModel):
    username: str = Field(validation_alias="user_name", serialization_alias="username")
    email: EmailStr
    birth_date: date | None = Field(
        default=None,
        validation_alias="date_of_birth",
        serialization_alias="birth_date",
    )

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
