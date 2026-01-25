from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Category
from app.auth.utils import admin_required

router = APIRouter(prefix="/categories", tags=["Categories"])


# ----- PUBLIC -----
@router.get("")
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).all()


# ----- ADMIN -----
@router.post("")
def create_category(
    name: str,
    db: Session = Depends(get_db),
    _=Depends(admin_required),
):
    existing = db.query(Category).filter(Category.name == name).first()

    if existing:
        raise HTTPException(400, "Category already exists")

    cat = Category(name=name)
    db.add(cat)
    db.commit()
    db.refresh(cat)

    return cat

