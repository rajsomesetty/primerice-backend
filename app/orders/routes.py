from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Address, Order, Cart, CartItem, User
from app.database import get_db
from app.deps import get_current_user
from app.auth.utils import admin_required
from datetime import datetime
import json

router = APIRouter(prefix="/orders", tags=["Orders"])


# ===================================================
# USER APIS (existing – untouched)
# ===================================================

@router.post("/address")
def save_address(body: dict, db: Session = Depends(get_db), user=Depends(get_current_user)):
    addr = Address(user_id=user.id, **body)
    db.add(addr)
    db.commit()
    db.refresh(addr)

    return addr


@router.get("/address")
def get_addresses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Address).filter(Address.user_id == user.id).all()


@router.post("/create")
def create_order(address_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    cart = db.query(Cart).filter(Cart.user_id == user.id).first()

    if not cart or not cart.items:
        raise HTTPException(400, "Cart is empty")

    address = db.query(Address).filter(
        Address.id == address_id,
        Address.user_id == user.id
    ).first()

    if not address:
        raise HTTPException(404, "Address not found")

    items_data = []
    total = 0

    for item in cart.items:
        items_data.append({
            "product_id": item.product_id,
            "name": item.product.name,
            "quantity": item.quantity,
            "price": item.product.price
        })
        total += item.quantity * item.product.price

    order = Order(
        user_id=user.id,
        items_json=json.dumps(items_data),
        total_price=total,
        address_id=address_id,
        created_at=datetime.utcnow(),
        status="PLACED"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.total_price = 0
    db.commit()

    return {"order_id": order.id, "total_price": total}


@router.get("/my")
def get_my_orders(db: Session = Depends(get_db), user=Depends(get_current_user)):
    orders = db.query(Order).filter(Order.user_id == user.id).order_by(Order.id.desc()).all()

    return [
        {
            "id": o.id,
            "created_at": o.created_at.isoformat(),
            "total": o.total_price,
            "status": o.status
        } for o in orders
    ]


@router.get("/{order_id}")
def get_order(order_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    address = db.query(Address).filter(Address.id == order.address_id).first()

    return {
        "id": order.id,
        "total": order.total_price,
        "status": order.status,
        "items": json.loads(order.items_json),
        "address": address,
        "created_at": order.created_at.isoformat()
    }


# ===================================================
# 🔐 ADMIN APIS
# ===================================================

@router.get("/all")
def admin_all_orders(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    result = []

    for o in orders:
        user = db.query(User).filter(User.id == o.user_id).first()

        result.append({
            "id": o.id,
            "total": o.total_price,
            "status": o.status,
            "created_at": o.created_at.isoformat(),
            "user": {
                "id": user.id,
                "name": user.name,
                "mobile": user.mobile
            }
        })

    return result


@router.patch("/{order_id}/status")
def update_status(
    order_id: int,
    body: dict,
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    order = db.query(Order).filter(Order.id == order_id).first()

    if not order:
        raise HTTPException(404, "Order not found")

    status = body.get("status")

    allowed = [
        "PLACED",
        "PROCESSING",
        "SHIPPED",
        "DELIVERED",
        "CANCELLED"
    ]

    if status not in allowed:
        raise HTTPException(400, "Invalid status")

    order.status = status
    db.commit()

    return {"message": "updated", "status": status}

