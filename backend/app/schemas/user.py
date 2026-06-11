"""User Pydantic schemas."""

import uuid
from datetime import datetime
from pydantic import BaseModel


class UserCreate(BaseModel):
    openid: str
    unionid: str | None = None


class RegisterRequest(BaseModel):
    email: str
    password: str
    verify_code: str
    nickname: str | None = None


class LoginRequest(BaseModel):
    email: str
    password: str


class UserRead(BaseModel):
    id: uuid.UUID
    openid: str | None = None
    email: str | None = None
    unionid: str | None = None
    phone: str | None = None
    nickname: str | None = None
    avatar_url: str | None = None
    role: str
    is_active: bool
    trial_used: bool
    xp: int = 0
    level: int = 1
    created_at: datetime

    model_config = {"from_attributes": True}


class UserUpdate(BaseModel):
    nickname: str | None = None
    avatar_url: str | None = None


class WechatLoginRequest(BaseModel):
    code: str


class WechatLoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserRead
