"""Auth Pydantic Schemas"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID


class UserRegister(BaseModel):
    email: EmailStr
    name: str
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class KakaoCallback(BaseModel):
    code: str


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: Optional[str] = None


class UserResponse(BaseModel):
    id: UUID
    email: str
    name: str
    provider: str
    role: str
    org_id: Optional[UUID] = None

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = None
