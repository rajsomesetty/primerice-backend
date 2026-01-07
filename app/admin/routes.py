from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Order, Address
from app.auth.utils import admin_required
import json

router = APIRouter(prefix="/admin", tags=["Admin"])


# 📌 Get all orders (with user, price & status)
@router.get("/orders")
def get_all_orders(user=Depends(admin_required), db: Session = Depends(get_db)):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    return [
        {
            "order_id": o.id,
            "total_price": o.total_price,
            "status": o.status,
            "customer": o.user.name if o.user else None,
            "created_at": o.created_at,
        }
        for o in orders
    ]


# 📌 Get full order details for admin view
@router.get("/orders/{order_id}")
def admin_order_details(order_id: int, user=Depends(admin_required), db: Session = Depends(get_db)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    address = db.query(Address).filter(Address.id == order.address_id).first()

    return {
        "order_id": order.id,
        "status": order.status,
        "total_price": order.total_price,
        "items": json.loads(order.items_json),
        "customer": order.user.name if order.user else None,
        "address": {
            "name": address.name,
            "mobile": address.mobile,
            "address_line": address.address_line,
            "city": address.city,
            "pincode": address.pincode,
        },
        "created_at": order.created_at,
    }


# 📌 Update order status
@router.patch("/orders/{order_id}/status")
def update_status(order_id: int, status: str, user=Depends(admin_required), db: Session = Depends(get_db)):
    if status not in ["Pending", "Delivered", "Cancelled"]:
        raise HTTPException(400, "Invalid status")

    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    order.status = status
    db.commit()
    return {"success": True, "new_status": status}

