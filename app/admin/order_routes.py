from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.database import get_db
from app.models import Order, User
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


# ✅ LIST ALL ORDERS
@router.get("")
def list_all_orders(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    result = []

    for o in orders:
        result.append({
            "order_id": o.id,
            "user_id": o.user_id,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "items": json.loads(o.items_json or "[]")
        })

    return result


# ✅ GET SINGLE ORDER
@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    o = db.query(Order).filter(Order.id == order_id).first()

    if not o:
        raise HTTPException(404, "Order not found")

    return {
        "order_id": o.id,
        "user_id": o.user_id,
        "total_price": o.total_price,
        "status": o.status,
        "created_at": o.created_at.isoformat(),
        "items": json.loads(o.items_json or "[]")
    }


# ✅ UPDATE STATUS
@router.put("/{order_id}/status")
def update_status(
    order_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    o = db.query(Order).filter(Order.id == order_id).first()

    if not o:
        raise HTTPException(404, "Order not found")

    o.status = body.get("status", o.status)

    db.commit()

    return {"message": "Status updated"}

