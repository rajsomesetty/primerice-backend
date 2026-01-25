from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/categories", tags=["Admin Categories"])


# ---------------- LIST ----------------
@router.get("")
def list_categories(
    db: Session = Depends(get_db),
    _=Depends(admin_required),
):
    return db.query(Category).order_by(Category.name).all()


# ---------------- CREATE ----------------
@router.post("")
def create_category(
    body: dict,
    db: Session = Depends(get_db),
    _=Depends(admin_required),
):
    name = body.get("name")

    if not name:
        raise HTTPException(400, "Category name required")

    exists = db.query(Category).filter(Category.name == name).first()
    if exists:
        raise HTTPException(400, "Category already exists")

    cat = Category(name=name.strip())

    db.add(cat)
    db.commit()
    db.refresh(cat)

    return cat


# ---------------- DELETE ----------------
@router.delete("/{cat_id}")
def delete_category(
    cat_id: int,
    db: Session = Depends(get_db),
    _=Depends(admin_required),
):
    cat = db.query(Category).filter(Category.id == cat_id).first()

    if not cat:
        raise HTTPException(404, "Category not found")

    db.delete(cat)
    db.commit()

    return {"status": "deleted"}

