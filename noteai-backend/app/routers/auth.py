from fastapi import APIRouter, HTTPException, Depends
from bson import ObjectId
from datetime import datetime, timezone

from app.schemas.user import UserRegister, UserLogin, TokenResponse, UserOut, RefreshRequest
from app.core.database import get_users_collection
from app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_refresh_token
)
from app.core.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


def serialize_user(user: dict) -> UserOut:
    return UserOut(id=str(user["_id"]), name=user["name"], email=user["email"])


# ── Register ─────────────────────────────────────────
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(body: UserRegister):
    users = get_users_collection()

    # Check duplicate email
    existing = await users.find_one({"email": body.email})
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")

    now = datetime.now(timezone.utc)
    user_doc = {
        "name":       body.name,
        "email":      body.email,
        "password":   hash_password(body.password),
        "created_at": now,
        "updated_at": now,
    }
    result = await users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id

    user_id = str(result.inserted_id)
    return TokenResponse(
        access_token=create_access_token({"sub": user_id}),
        refresh_token=create_refresh_token({"sub": user_id}),
        user=serialize_user(user_doc),
    )


# ── Login ─────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(body: UserLogin):
    users = get_users_collection()

    user = await users.find_one({"email": body.email})
    if not user or not verify_password(body.password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    user_id = str(user["_id"])
    return TokenResponse(
        access_token=create_access_token({"sub": user_id}),
        refresh_token=create_refresh_token({"sub": user_id}),
        user=serialize_user(user),
    )


# ── Refresh Token ─────────────────────────────────────
@router.post("/refresh")
async def refresh(body: RefreshRequest):
    payload = decode_refresh_token(body.refresh_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    return {
        "access_token": create_access_token({"sub": user_id}),
        "token_type": "bearer"
    }


# ── Me (current user) ─────────────────────────────────
@router.get("/me", response_model=UserOut)
async def me(current_user: dict = Depends(get_current_user)):
    return serialize_user(current_user)
