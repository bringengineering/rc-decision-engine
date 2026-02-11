"""Auth service: JWT, password hashing, Kakao OAuth."""

from datetime import datetime, timedelta, timezone
from uuid import UUID

import httpx
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.db.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    payload = {"sub": str(user_id), "exp": expire}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


async def register_user(db: AsyncSession, email: str, name: str, password: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        provider="local",
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user and user.password_hash and verify_password(password, user.password_hash):
        user.last_login = datetime.now(timezone.utc)
        return user
    return None


async def get_or_create_kakao_user(db: AsyncSession, code: str, redirect_uri: str | None = None) -> User:
    """Exchange Kakao auth code for user info, create user if needed."""
    token_url = "https://kauth.kakao.com/oauth/token"
    token_data = {
        "grant_type": "authorization_code",
        "client_id": settings.KAKAO_CLIENT_ID,
        "redirect_uri": redirect_uri or settings.KAKAO_REDIRECT_URI,
        "code": code,
    }
    if settings.KAKAO_CLIENT_SECRET:
        token_data["client_secret"] = settings.KAKAO_CLIENT_SECRET

    async with httpx.AsyncClient() as client:
        token_resp = await client.post(token_url, data=token_data)
        token_resp.raise_for_status()
        access_token = token_resp.json()["access_token"]

        user_resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_resp.raise_for_status()
        kakao_user = user_resp.json()

    kakao_id = str(kakao_user["id"])
    kakao_account = kakao_user.get("kakao_account", {})
    email = kakao_account.get("email", f"kakao_{kakao_id}@kakao.com")
    nickname = kakao_account.get("profile", {}).get("nickname", f"User_{kakao_id}")

    result = await db.execute(
        select(User).where((User.provider == "kakao") & (User.provider_id == kakao_id))
    )
    user = result.scalar_one_or_none()
    if not user:
        user = User(email=email, name=nickname, provider="kakao", provider_id=kakao_id)
        db.add(user)
        await db.flush()
    user.last_login = datetime.now(timezone.utc)
    return user
