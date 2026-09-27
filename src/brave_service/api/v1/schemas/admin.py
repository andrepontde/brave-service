from pydantic import BaseModel, ConfigDict, EmailStr, Field


class AdminCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=8, max_length=255)


class AdminUpdate(BaseModel):
    email: EmailStr | None = None
    password: str | None = Field(default=None, min_length=8, max_length=255)


class AdminResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr