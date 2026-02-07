"""Auth Service — JWT, password hashing, Kakao OAuth"""

from datetime import datetime, timedelta, timezone
from typing import Optional
from uuid import UUID

from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import httpx

from app.config import settings
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode = {"sub": str(user_id), "exp": expire}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_access_token(token: str) -> Optional[str]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload.get("sub")
    except JWTError:
        return None


async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> Optional[User]:
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, email: str, name: str, password: str) -> User:
    user = User(
        email=email,
        name=name,
        password_hash=hash_password(password),
        provider="local",
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, email: str, password: str) -> Optional[User]:
    user = await get_user_by_email(db, email)
    if not user or not user.password_hash:
        return None
    if not verify_password(password, user.password_hash):
        return None
    user.last_login = datetime.utcnow()
    await db.commit()
    return user


async def kakao_get_user_info(access_token: str) -> dict:
    """카카오 API에서 사용자 정보 가져오기"""
    async with httpx.AsyncClient() as client:
        resp = await client.get(
            "https://kapi.kakao.com/v2/user/me",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        resp.raise_for_status()
        return resp.json()


async def kakao_get_token(code: str) -> str:
    """카카오 인증 코드로 access_token 교환"""
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            "https://kauth.kakao.com/oauth/token",
            data={
                "grant_type": "authorization_code",
                "client_id": settings.KAKAO_CLIENT_ID,
                "redirect_uri": settings.KAKAO_REDIRECT_URI,
                "code": code,
            },
        )
        resp.raise_for_status()
        return resp.json()["access_token"]


async def get_or_create_kakao_user(db: AsyncSession, kakao_info: dict) -> User:
    """카카오 사용자 조회 or 생성"""
    kakao_id = str(kakao_info["id"])
    kakao_account = kakao_info.get("kakao_account", {})
    email = kakao_account.get("email", f"kakao_{kakao_id}@kakao.local")
    name = kakao_account.get("profile", {}).get("nickname", f"User_{kakao_id}")

    # 기존 사용자 확인 (provider_id로)
    result = await db.execute(
        select(User).where(User.provider == "kakao", User.provider_id == kakao_id)
    )
    user = result.scalar_one_or_none()

    if user:
        user.last_login = datetime.utcnow()
        await db.commit()
        return user

    # 이메일로 기존 사용자 확인
    user = await get_user_by_email(db, email)
    if user:
        user.provider = "kakao"
        user.provider_id = kakao_id
        user.last_login = datetime.utcnow()
        await db.commit()
        return user

    # 새 사용자 생성
    user = User(
        email=email,
        name=name,
        provider="kakao",
        provider_id=kakao_id,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
