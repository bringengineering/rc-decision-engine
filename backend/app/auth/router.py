"""Auth API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.postgres import get_db
from app.dependencies import get_current_user
from app.db.models import User
from app.auth.schemas import UserRegister, UserLogin, KakaoAuthRequest, Token, UserResponse
from app.auth.service import register_user, authenticate_user, create_access_token, get_or_create_kakao_user

router = APIRouter()


@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user with email/password."""
    try:
        user = await register_user(db, data.email, data.name, data.password)
        token = create_access_token(user.id)
        return Token(access_token=token)
    except Exception:
        raise HTTPException(status_code=400, detail="Email already registered")


@router.post("/login", response_model=Token)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login with email/password."""
    user = await authenticate_user(db, data.email, data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    token = create_access_token(user.id)
    return Token(access_token=token)


@router.post("/kakao", response_model=Token)
async def kakao_auth(data: KakaoAuthRequest, db: AsyncSession = Depends(get_db)):
    """Login/Register via Kakao OAuth."""
    try:
        user = await get_or_create_kakao_user(db, data.code, data.redirect_uri)
        token = create_access_token(user.id)
        return Token(access_token=token)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Kakao auth failed: {e}")


@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user info."""
    return current_user
