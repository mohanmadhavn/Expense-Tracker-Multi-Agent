from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from sqlalchemy import text

from app.database.connection import SessionLocal
from app.auth.password import hash_password, verify_password
from app.auth.jwt_handler import create_access_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


class RegisterRequest(BaseModel):
    name: str
    email: str
    password: str


class LoginRequest(BaseModel):
    email: str
    password: str


@router.post("/register")
def register(request: RegisterRequest):
    db = SessionLocal()

    try:
        existing_user = db.execute(
            text("SELECT user_id FROM users WHERE email = :email"),
            {"email": request.email},
        ).fetchone()

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")

        password_hash = hash_password(request.password)

        result = db.execute(
            text(
                """
                INSERT INTO users (name, email, password_hash, role, status)
                VALUES (:name, :email, :password_hash, 'USER', 'ACTIVE')
                RETURNING user_id
                """
            ),
            {
                "name": request.name,
                "email": request.email,
                "password_hash": password_hash,
            },
        ).fetchone()

        db.commit()

        return {"message": "User registered successfully", "user_id": result.user_id}

    finally:
        db.close()


@router.post("/login")
def login(request: LoginRequest):
    db = SessionLocal()

    try:
        user = db.execute(
            text(
                "SELECT user_id, password_hash, role, status FROM users WHERE email = :email"
            ),
            {"email": request.email},
        ).fetchone()

        if not user:
            raise HTTPException(status_code=401, detail="Invalid email or password")

        if user.status != "ACTIVE":
            raise HTTPException(status_code=403, detail="Account is not active")

        if not verify_password(request.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid email or password")

        token = create_access_token(user_id=user.user_id, role=user.role)

        return {"access_token": token, "token_type": "bearer"}

    finally:
        db.close()
