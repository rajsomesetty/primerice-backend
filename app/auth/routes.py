from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth.utils import (
    hash_password,
    verify_password,
    create_access_token,
)
from app.schemas import SignupRequest, LoginRequest

router = APIRouter(prefix="/auth")


# --------------------
# DB Dependency
# --------------------
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# --------------------
# SIGNUP
# --------------------
@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.mobile == data.mobile).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Mobile already registered"
        )

    # 🔒 bcrypt safety (72-byte max)
    try:
        hashed_password = hash_password(data.password)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )

    user = User(
        name=data.name,
        mobile=data.mobile,
        password=hashed_password,
        role="user",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # ✅ CORRECT TOKEN CREATION
    token = create_access_token(user.id, user.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "role": user.role,
        },
    }


# --------------------
# LOGIN
# --------------------
@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == data.mobile).first()

    if not user or not verify_password(data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Invalid mobile or password"
        )

    # ✅ SAME TOKEN LOGIC AS SIGNUP
    token = create_access_token(user.id, user.role)

    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "role": user.role,
        },
    }

