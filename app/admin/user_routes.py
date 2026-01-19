from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/users", tags=["Admin Users"])


# ✅ LIST USERS
@router.get("")
def list_users(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    return db.query(User).order_by(User.id.desc()).all()


# ✅ MAKE ADMIN
@router.post("/{user_id}/make-admin")
def make_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    user.role = "admin"
    db.commit()

    return {"message": "User promoted to admin"}


# ✅ REMOVE ADMIN
@router.post("/{user_id}/remove-admin")
def remove_admin(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    user.role = "user"
    db.commit()

    return {"message": "Admin role removed"}


# ❌ DELETE USER
@router.delete("/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    user = db.query(User).get(user_id)

    if not user:
        raise HTTPException(404, "User not found")

    db.delete(user)
    db.commit()

    return {"message": "User deleted"}

