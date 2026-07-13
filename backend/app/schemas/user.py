from datetime import datetime
from pydantic import BaseModel, EmailStr, ConfigDict
from app.models.user import UserRoleEnum

class UserBase(BaseModel):
    email: EmailStr
    name: str
    phone: str | None = None
    role: UserRoleEnum = UserRoleEnum.Citizen
    department_id: int | None = None

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    name: str | None = None
    phone: str | None = None
    role: UserRoleEnum | None = None
    department_id: int | None = None
    password: str | None = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    user_id: int
    created_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)
