from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session, joinedload
import os
import shutil

from app.database import get_db
from app.models import Product, Category
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/products", tags=["Admin Products"])

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


# ---------------- LIST ----------------

@router.get("")
def list_products(
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .all()
    )


# ---------------- ADD ----------------

@router.post("")
def add_product(
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    image_url = None

    if image:
        filename = image.filename
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        image_url = f"/uploads/{filename}"

    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(400, "Invalid category")

    product = Product(
        name=name,
        price=price,
        description=description,
        image_url=image_url,
        category_id=category_id,
    )

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


# ---------------- UPDATE ----------------

@router.put("/{product_id}")
def update_product(
    product_id: int,
    name: str = Form(...),
    price: float = Form(...),
    description: str = Form(""),
    category_id: int = Form(...),
    image: UploadFile | None = File(None),
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(404, "Product not found")

    product.name = name
    product.price = price
    product.description = description
    product.category_id = category_id

    if image:
        filename = image.filename
        path = os.path.join(UPLOAD_DIR, filename)

        with open(path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)

        product.image_url = f"/uploads/{filename}"

    db.commit()
    db.refresh(product)

    return product


# ---------------- DELETE ----------------

@router.delete("/{product_id}")
def delete_product(
    product_id: int,
    db: Session = Depends(get_db),
    _: str = Depends(admin_required),
):
    product = db.query(Product).filter(Product.id == product_id).first()

    if not product:
        raise HTTPException(404, "Not found")

    db.delete(product)
    db.commit()

    return {"success": True}

