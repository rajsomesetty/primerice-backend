from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Address
from app.deps import get_user

router = APIRouter(prefix="/addresses")

def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()

@router.get("")
def list_addresses(user=Depends(get_user), db: Session = Depends(db)):
    return db.query(Address).filter_by(user_id=user["id"]).all()

@router.post("")
def add_address(data: dict, user=Depends(get_user), db: Session = Depends(db)):
    addr = Address(user_id=user["id"], **data)
    db.add(addr)
    db.commit()
    return addr

