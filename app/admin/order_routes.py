from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models import Order, User, Address
from app.auth.utils import admin_required
import json

router = APIRouter(prefix="/admin/orders", tags=["Admin Orders"])


# ================= LIST ORDERS =================

@router.get("")
def list_orders(status: str | None = None, db: Session = Depends(get_db), _=Depends(admin_required)):
    q = db.query(Order).options(joinedload(Order.user), joinedload(Order.address))

    if status:
        q = q.filter(Order.status == status)

    orders = q.order_by(Order.id.desc()).all()

    return [
        {
            "id": o.id,
            "total": o.total_price,
            "status": o.status,
            "tracking_number": o.tracking_number,
            "created_at": o.created_at,
            "user": {
                "name": o.user.name,
                "mobile": o.user.mobile,
            },
            "address": {
                "name": o.address.name,
                "mobile": o.address.mobile,
                "address_line": o.address.address_line,
                "city": o.address.city,
                "pincode": o.address.pincode,
            },
            "items": json.loads(o.items_json),
        }
        for o in orders
    ]


# ================= UPDATE STATUS =================

@router.put("/{order_id}/status")
def update_status(order_id: int, status: str, db: Session = Depends(get_db), _=Depends(admin_required)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    order.status = status
    db.commit()

    return {"success": True}


# ================= UPDATE TRACKING =================

@router.put("/{order_id}/tracking")
def update_tracking(order_id: int, tracking: str, db: Session = Depends(get_db), _=Depends(admin_required)):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    order.tracking_number = tracking
    db.commit()

    return {"success": True}

