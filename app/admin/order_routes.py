from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json
from datetime import datetime

from app.database import get_db
from app.models import Order, User, Address
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


# ✅ LIST WITH FILTERS
@router.get("")
def list_orders(
    status: str | None = None,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    q = db.query(Order)

    if status:
        q = q.filter(Order.status == status)

    orders = q.order_by(Order.id.desc()).all()

    result = []
    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()
        addr = db.query(Address).filter(Address.id == o.address_id).first()

        result.append({
            "order_id": o.id,
            "total_price": o.total_price,
            "status": o.status,
            "tracking_number": o.tracking_number,
            "created_at": o.created_at.isoformat(),

            "user": {
                "name": user.name,
                "mobile": user.mobile
            },

            "address": {
                "name": addr.name,
                "mobile": addr.mobile,
                "address_line": addr.address_line,
                "city": addr.city,
                "pincode": addr.pincode
            },

            "items": json.loads(o.items_json or "[]")
        })

    return result


# ✅ UPDATE STATUS + TRACKING
@router.put("/{order_id}")
def update_order(
    order_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    o = db.query(Order).filter(Order.id == order_id).first()

    if not o:
        raise HTTPException(404, "Order not found")

    o.status = body.get("status", o.status)
    o.tracking_number = body.get("tracking_number", o.tracking_number)

    db.commit()

    return {"message": "updated"}


# ✅ REVENUE STATS
@router.get("/stats")
def stats(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required),
):
    orders = db.query(Order).all()

    total = sum(o.total_price for o in orders)

    return {
        "total_orders": len(orders),
        "revenue": total,
        "pending": len([o for o in orders if o.status == "Pending"]),
        "shipped": len([o for o in orders if o.status == "Shipped"]),
    }

