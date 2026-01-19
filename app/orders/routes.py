from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Address, Order, Cart, CartItem, User
from app.database import get_db
from app.deps import get_current_user
from app.auth.utils import admin_required
from datetime import datetime
import json

router = APIRouter(prefix="/orders", tags=["Orders"])


# ====================================================
# 1) ADMIN ROUTES — MUST COME FIRST (STATIC PATHS)
# ====================================================

@router.get("/all")
def admin_all_orders(
    db: Session = Depends(get_db),
    _: User = Depends(admin_required)
):
    orders = db.query(Order).order_by(Order.id.desc()).all()

    return [
        {
            "order_id": o.id,
            "user_id": o.user_id,
            "total_price": o.total_price,
            "status": o.status,
            "created_at": o.created_at.isoformat()
        }
        for o in orders
    ]


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

    order.status = body.get("status", order.status)

    db.commit()
    db.refresh(order)

    return {"message": "Status updated", "status": order.status}


# ====================================================
# 2) USER ADDRESS ROUTES
# ====================================================

@router.post("/address")
def save_address(
    body: dict,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    addr = Address(user_id=user.id, **body)

    db.add(addr)
    db.commit()
    db.refresh(addr)

    return {
        "id": addr.id,
        "name": addr.name,
        "mobile": addr.mobile,
        "address_line": addr.address_line,
        "city": addr.city,
        "pincode": addr.pincode
    }


@router.get("/address")
def get_addresses(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return db.query(Address).filter(Address.user_id == user.id).all()


# ====================================================
# 3) CREATE ORDER
# ====================================================

@router.post("/create")
def create_order(
    address_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
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
        status="Pending"
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    # Clear cart
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    cart.total_price = 0
    db.commit()

    return {"order_id": order.id, "total_price": total}


# ====================================================
# 4) USER ORDERS LIST
# ====================================================

@router.get("/my")
def get_my_orders(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.user_id == user.id
    ).order_by(Order.id.desc()).all()

    return [
        {
            "order_id": o.id,
            "created_at": o.created_at.isoformat(),
            "total_price": o.total_price,
            "status": o.status
        }
        for o in orders
    ]


# ====================================================
# 5) SINGLE ORDER — KEEP THIS LAST 🔥
# ====================================================

@router.get("/{order_id}")
def get_order(
    order_id: int,
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == user.id
    ).first()

    if not order:
        raise HTTPException(404, "Order not found")

    address = db.query(Address).filter(
        Address.id == order.address_id
    ).first()

    return {
        "order_id": order.id,
        "total_price": order.total_price,
        "status": order.status,
        "items": json.loads(order.items_json),
        "address": {
            "name": address.name,
            "mobile": address.mobile,
            "address_line": address.address_line,
            "city": address.city,
            "pincode": address.pincode
        },
        "created_at": order.created_at.isoformat()
    }

