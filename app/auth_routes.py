from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth.utils import hash_password, verify_password, create_access_token
from app.schemas import SignupRequest, LoginRequest

router = APIRouter(prefix="/auth")


def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(db)):
    existing = db.query(User).filter(User.mobile == data.mobile).first()
    if existing:
        raise HTTPException(status_code=400, detail="Mobile already registered")

    user = User(
        name=data.name,
        mobile=data.mobile,
        password=hash_password(data.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"message": "Signup success"}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(db)):
    user = db.query(User).filter(User.mobile == data.mobile).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid mobile or password")

    token = create_access_token({
        "user_id": user.id,
        "role": user.role
    })


    return {
        "access_token": token,
        "user": {
            "id": user.id,
            "name": user.name,
            "mobile": user.mobile,
            "role": user.role
        }
    }


