from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlalchemy.orm import Session
import os
import shutil

from app.database import SessionLocal
from app.models import Product
from app.deps import admin_only

router = APIRouter(prefix="/admin/products")

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# DB dependency
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# =========================
# GET PRODUCTS
# =========================
@router.get("")
def list_products(
    db: Session = Depends(db),
    _=Depends(admin_only)
):
    return db.query(Product).all()


# =========================
# ADD PRODUCT (FIXED)
# =========================
@router.post("")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(db),
    _=Depends(admin_only)
):
    image_url = "default.jpg"

    if image:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        image_url = f"/{UPLOAD_DIR}/{image.filename}"

    product = Product(
        name=name,
        price=price,
        description=description,
        image_url=image_url
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# =========================
# UPDATE PRODUCT (IMPORTANT)
# =========================
@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(db),
    _=Depends(admin_only)
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        return {"error": "Product not found"}

    product.name = name
    product.price = price
    product.description = description

    if image:
        file_path = os.path.join(UPLOAD_DIR, image.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)
        product.image_url = f"/{UPLOAD_DIR}/{image.filename}"

    db.commit()
    db.refresh(product)

    return product

