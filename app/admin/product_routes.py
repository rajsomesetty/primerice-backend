from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Product
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/products", tags=["Admin - Products"])

# ✔️ Create product
@router.post("")
def create_product(data: dict, user=Depends(admin_required), db: Session = Depends(get_db)):
    product = Product(
        name=data["name"],
        price=data["price"],
        image_url=data.get("image_url", "")
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return {"success": True}

# ✔️ Update product
@router.put("/{product_id}")
def update_product(product_id: int, data: dict, user=Depends(admin_required), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    product.name = data["name"]
    product.price = data["price"]
    product.image_url = data.get("image_url", "")
    db.commit()
    return {"success": True}

# ✔️ Delete product
@router.delete("/{product_id}")
def delete_product(product_id: int, user=Depends(admin_required), db: Session = Depends(get_db)):
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        raise HTTPException(404, "Product not found")

    db.delete(product)
    db.commit()
    return {"success": True}

