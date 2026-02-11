"""Auth request/response schemas."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class KakaoAuthRequest(BaseModel):
    code: str
    redirect_uri: Optional[str] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    provider: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}
