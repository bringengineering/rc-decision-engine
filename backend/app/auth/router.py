"""Auth API Router"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth import schemas, service

router = APIRouter(prefix="/api/auth", tags=["auth"])
security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Dependency: extract current user from JWT token"""
    user_id = service.decode_access_token(credentials.credentials)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    user = await service.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user


@router.post("/register", response_model=schemas.Token)
async def register(data: schemas.UserRegister, db: AsyncSession = Depends(get_db)):
    existing = await service.get_user_by_email(db, data.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = await service.create_user(db, data.email, data.name, data.password)
    token = service.create_access_token(str(user.id))
    return schemas.Token(access_token=token)


@router.post("/login", response_model=schemas.Token)
async def login(data: schemas.UserLogin, db: AsyncSession = Depends(get_db)):
    user = await service.authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = service.create_access_token(str(user.id))
    return schemas.Token(access_token=token)


@router.post("/kakao", response_model=schemas.Token)
async def kakao_login(data: schemas.KakaoCallback, db: AsyncSession = Depends(get_db)):
    try:
        kakao_token = await service.kakao_get_token(data.code)
        kakao_info = await service.kakao_get_user_info(kakao_token)
        user = await service.get_or_create_kakao_user(db, kakao_info)
        token = service.create_access_token(str(user.id))
        return schemas.Token(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kakao login failed: {str(e)}")


@router.get("/me", response_model=schemas.UserResponse)
async def get_me(current_user=Depends(get_current_user)):
    return current_user
