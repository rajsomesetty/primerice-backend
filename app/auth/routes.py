from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import User
from app.auth.utils import hash_password, verify_password, create_access_token
from app.schemas import SignupRequest, LoginRequest

router = APIRouter(prefix="/auth")  # IMPORTANT!!

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.post("/signup")
def signup(data: SignupRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.mobile == data.mobile).first()
    if existing:
        raise HTTPException(400, "Mobile already registered")

    user = User(
        name=data.name,
        mobile=data.mobile,
        password=hash_password(data.password),
        role="user"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    return {"id": user.id, "name": user.name, "mobile": user.mobile}


@router.post("/login")
def login(data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.mobile == data.mobile).first()
    if not user or not verify_password(data.password, user.password):
        raise HTTPException(401, "Invalid mobile or password")

    token = create_access_token(user.id, user.role)
    return {"access_token": token, "token_type": "bearer"}

