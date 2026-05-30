from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from app.models.user import UserRole


class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.TRAINER


class UserCreate(UserBase):
    password: Optional[str] = None
    google_id: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None
    avatar_url: Optional[str] = None


class UserOut(UserBase):
    id: str
    avatar_url: Optional[str] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class TokenData(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut


class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None
