from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import httpx
import asyncio
from app.services.backup import run_backup

from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserOut, TokenData, GoogleAuthRequest
from app.core.auth import create_access_token, hash_password, verify_password
from app.config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenData)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not user.hashed_password or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account deactivated")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenData(access_token=token, user=UserOut.model_validate(user))


@router.post("/google", response_model=TokenData)
async def google_login(body: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    try:
        async with httpx.AsyncClient() as client:
            token_resp = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "code": body.code,
                    "client_id": settings.GOOGLE_CLIENT_ID,
                    "client_secret": settings.GOOGLE_CLIENT_SECRET,
                    "redirect_uri": body.redirect_uri or settings.GOOGLE_REDIRECT_URI,
                    "grant_type": "authorization_code",
                },
            )
            token_data = token_resp.json()

        id_info = id_token.verify_oauth2_token(
            token_data["id_token"],
            google_requests.Request(),
            settings.GOOGLE_CLIENT_ID,
        )

        google_id = id_info["sub"]
        email = id_info["email"]
        full_name = id_info.get("name", email.split("@")[0])
        avatar_url = id_info.get("picture", "")

        result = await db.execute(select(User).where(User.google_id == google_id))
        user = result.scalar_one_or_none()

        if not user:
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

        if not user:
            # Auto-create as ADMIN for first user, TRAINER otherwise
            all_users = await db.execute(select(User))
            is_first = len(all_users.scalars().all()) == 0
            user = User(
                email=email,
                full_name=full_name,
                avatar_url=avatar_url,
                google_id=google_id,
                role=UserRole.ADMIN if is_first else UserRole.TRAINER,
            )
            db.add(user)
            await db.commit()
            await db.refresh(user)
        else:
            user.google_id = google_id
            user.avatar_url = avatar_url
            await db.commit()

        token = create_access_token({"sub": str(user.id), "role": user.role.value})
        return TokenData(access_token=token, user=UserOut.model_validate(user))

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Google auth failed: {str(e)}")


@router.post("/register", response_model=TokenData, status_code=201)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == user_in.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=hash_password(user_in.password) if user_in.password else None,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    # Auto-backup after new user registered
    asyncio.get_event_loop().run_in_executor(None, run_backup, f"user_registered:{user.email}")

    token = create_access_token({"sub": str(user.id), "role": user.role.value})
    return TokenData(access_token=token, user=UserOut.model_validate(user))


@router.get("/me", response_model=UserOut)
async def get_me(db: AsyncSession = Depends(get_db)):
    pass  # handled via dependency injection in real usage
