from datetime import datetime, timezone

from bson import ObjectId
from fastapi import APIRouter, HTTPException, status

from auth import create_access_token, hash_password, verify_password
from database import get_database
from schemas import TokenResponse, UserLogin, UserRegister

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register(payload: UserRegister) -> TokenResponse:
    db = get_database()

    existing_user = db.users.find_one({"email": payload.email.lower()})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    user_document = {
        "username": payload.username.strip(),
        "email": payload.email.lower(),
        "hashed_password": hash_password(payload.password),
        "created_at": datetime.now(timezone.utc),
    }

    result = db.users.insert_one(user_document)
    access_token = create_access_token(str(result.inserted_id))

    return TokenResponse(access_token=access_token)


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin) -> TokenResponse:
    db = get_database()
    user = db.users.find_one({"email": payload.email.lower()})

    if not user or not verify_password(payload.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    access_token = create_access_token(str(user["_id"]))
    return TokenResponse(access_token=access_token)
