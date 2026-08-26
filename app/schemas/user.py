from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.user import RoleEnum


class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    role: RoleEnum = RoleEnum.USER
    is_active: bool = True


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, max_length=128)


class UserRegister(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserUpdate(BaseModel):
    full_name: str | None = Field(None, min_length=2, max_length=100)
    role: RoleEnum | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CurrentUser(BaseModel):
    id: int
    role: str
    is_active: bool
