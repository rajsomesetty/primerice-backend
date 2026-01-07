from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Product
from app.deps import admin_only
import shutil

router = APIRouter(prefix="/admin/products")

def db():
    d = SessionLocal()
    try:
        yield d
    finally:
        d.close()

@router.get("")
def list_products(db: Session = Depends(db), _=Depends(admin_only)):
    return db.query(Product).all()

@router.post("")
def add_product(data: dict, db: Session = Depends(db), _=Depends(admin_only)):
    p = Product(**data)
    db.add(p)
    db.commit()
    return p

@router.post("/upload")
def upload_image(file: UploadFile = File(...), _=Depends(admin_only)):
    path = f"uploads/{file.filename}"
    with open(path, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"path": path}

