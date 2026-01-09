from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session
import os
import shutil

from app.database import SessionLocal
from app.models import Product
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


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
# LIST PRODUCTS
# --------------------
@router.get("")
def list_products(
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    return db.query(Product).all()


# --------------------
# ADD PRODUCT
# --------------------
@router.post("")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    image_url = None

    if image:
        filename = image.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/uploads/{filename}"

    product = Product(
        name=name,
        price=price,
        description=description,
        image_url=image_url,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# --------------------
# UPDATE PRODUCT
# --------------------
@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product.name = name
    product.price = price
    product.description = description

    if image:
        filename = image.filename
        file_path = os.path.join(UPLOAD_DIR, filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        product.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)

    return product

