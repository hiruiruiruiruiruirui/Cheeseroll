"""Authentication endpoints — login, register, profile."""

import uuid
import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jose import jwt

from ..deps import get_db, get_current_user
from ...config import settings
from ...models.user import User
from ...schemas.user import (
    WechatLoginRequest, WechatLoginResponse, UserRead, UserUpdate,
    RegisterRequest, LoginRequest,
)
from ...utils.wechat import code_to_session

router = APIRouter()

# In-memory verification codes store (use Redis in production)
_verification_codes: dict[str, str] = {}


def _hash_password(password: str) -> str:
    salt = settings.SECRET_KEY[:32].encode()
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000).hex()


def _verify_password(password: str, hashed: str) -> bool:
    return _hash_password(password) == hashed


def _generate_code() -> str:
    return str(secrets.randbelow(900000) + 100000)


@router.post("/auth/send-code")
async def send_verification_code(email: str = "", db: AsyncSession = Depends(get_db)):
    """Send email verification code. In dev mode, returns the code directly."""
    if not email or "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")

    code = _generate_code()
    _verification_codes[email] = code

    if settings.APP_ENV == "development":
        return {"message": "Code generated", "code": code, "email": email}

    # TODO: Send actual email via SMTP/SendGrid here
    return {"message": "Verification code sent", "email": email}


@router.post("/auth/register", response_model=WechatLoginResponse)
async def register(
    req: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """Register with email, password, and verification code."""
    # Verify code
    stored = _verification_codes.get(req.email)
    if not stored or stored != req.verify_code:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")

    existing = await db.execute(select(User).where(User.email == req.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        openid=f"email:{req.email}",
        email=req.email,
        password_hash=_hash_password(req.password),
        nickname=req.nickname or req.email.split("@")[0],
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Clear verification code
    _verification_codes.pop(req.email, None)

    token = _create_jwt(user.id)
    return WechatLoginResponse(
        access_token=token, token_type="bearer",
        user=UserRead(
            id=user.id, openid=user.openid, email=user.email, unionid=user.unionid,
            phone=user.phone, nickname=user.nickname, avatar_url=user.avatar_url,
            role=user.role, is_active=user.is_active, trial_used=user.trial_used,
            created_at=user.created_at,
        ),
    )


@router.post("/auth/login", response_model=WechatLoginResponse)
async def login(
    req: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login with email and password."""
    result = await db.execute(select(User).where(User.email == req.email))
    user = result.scalar_one_or_none()

    if not user or not user.password_hash or not _verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = _create_jwt(user.id)
    return WechatLoginResponse(
        access_token=token, token_type="bearer",
        user=UserRead(
            id=user.id, openid=user.openid, email=user.email, unionid=user.unionid,
            phone=user.phone, nickname=user.nickname, avatar_url=user.avatar_url,
            role=user.role, is_active=user.is_active, trial_used=user.trial_used,
            created_at=user.created_at,
        ),
    )


@router.post("/auth/dev-login", response_model=WechatLoginResponse)
async def dev_login(
    db: AsyncSession = Depends(get_db),
):
    """Dev-only login — creates a developer account with unlimited access."""
    if settings.APP_ENV != "development":
        raise HTTPException(status_code=404, detail="Not found")

    dev_email = "dev@cheeseroll.com"
    result = await db.execute(select(User).where(User.email == dev_email))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            openid="dev_user", email=dev_email, password_hash=_hash_password("dev123456"),
            nickname="Developer", role="admin", trial_used=False,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    elif not user.password_hash:
        user.password_hash = _hash_password("dev123456")
        user.role = "admin"
        await db.commit()
        await db.refresh(user)

    token = _create_jwt(user.id)
    return WechatLoginResponse(
        access_token=token, token_type="bearer",
        user=UserRead(
            id=user.id, openid=user.openid, email=user.email, unionid=user.unionid,
            phone=user.phone, nickname=user.nickname, avatar_url=user.avatar_url,
            role=user.role, is_active=user.is_active, trial_used=user.trial_used,
            created_at=user.created_at,
        ),
    )


def _create_jwt(user_id: uuid.UUID) -> str:
    """Create a JWT access token for a user."""
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {
        "sub": str(user_id),
        "exp": expire,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


@router.post("/auth/wechat-login", response_model=WechatLoginResponse)
async def wechat_login(
    req: WechatLoginRequest,
    db: AsyncSession = Depends(get_db),
):
    """Login via WeChat Mini Program code.

    Exchanges the temporary code for openid, creates or finds the user,
    and returns a JWT access token.
    """
    # Exchange code for WeChat session
    try:
        wx_session = await code_to_session(req.code)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )

    openid = wx_session["openid"]

    # Find existing user or create new one
    result = await db.execute(select(User).where(User.openid == openid))
    user = result.scalar_one_or_none()

    if not user:
        user = User(
            openid=openid,
            unionid=wx_session.get("unionid"),
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    # Generate JWT
    token = _create_jwt(user.id)

    return WechatLoginResponse(
        access_token=token,
        token_type="bearer",
        user=UserRead(
            id=user.id,
            openid=user.openid,
            unionid=user.unionid,
            phone=user.phone,
            nickname=user.nickname,
            avatar_url=user.avatar_url,
            role=user.role,
            is_active=user.is_active,
            trial_used=user.trial_used,
            created_at=user.created_at,
        ),
    )


@router.get("/auth/me", response_model=UserRead)
async def get_profile(
    current_user: User = Depends(get_current_user),
):
    """Get current user profile."""
    return UserRead(
        id=current_user.id,
        openid=current_user.openid,
        unionid=current_user.unionid,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_active=current_user.is_active,
        trial_used=current_user.trial_used,
        created_at=current_user.created_at,
    )


CHEESE_ACHIEVEMENTS = {
    5: "芝士条", 10: "芝士片", 20: "芝士球", 35: "芝士棒", 50: "芝士蛋糕",
    70: "芝士火锅", 100: "芝士拼盘", 150: "芝士焗饭", 200: "芝士披萨",
    300: "芝士千层", 450: "芝士熔岩", 600: "芝士天堂", 800: "芝士宇宙", 999: "芝士之神"
}

@router.post("/auth/xp")
async def add_xp(amount: int = 38, user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Add XP and handle level ups."""
    user.xp += amount
    old_level = user.level
    user.level = min(999, (user.xp // 50) + 1)
    leveled_up = user.level > old_level
    achievement = CHEESE_ACHIEVEMENTS.get(user.level) if leveled_up else None
    await db.commit()
    return {"xp": user.xp, "level": user.level, "leveled_up": leveled_up, "achievement": achievement}


@router.put("/auth/me", response_model=UserRead)
async def update_profile(
    update: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update user profile (nickname, avatar)."""
    if update.nickname is not None:
        current_user.nickname = update.nickname
    if update.avatar_url is not None:
        current_user.avatar_url = update.avatar_url

    await db.commit()
    await db.refresh(current_user)

    return UserRead(
        id=current_user.id,
        openid=current_user.openid,
        unionid=current_user.unionid,
        phone=current_user.phone,
        nickname=current_user.nickname,
        avatar_url=current_user.avatar_url,
        role=current_user.role,
        is_active=current_user.is_active,
        trial_used=current_user.trial_used,
        created_at=current_user.created_at,
    )
