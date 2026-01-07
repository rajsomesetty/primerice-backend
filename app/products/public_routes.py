from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product

router = APIRouter(prefix="/products")

def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()

@router.get("")
def list_products(db: Session = Depends(db)):
    return db.query(Product).all()

