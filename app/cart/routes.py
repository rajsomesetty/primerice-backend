from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Cart, CartItem, Product
from app.database import get_db
from app.auth.utils import get_user

router = APIRouter(prefix="/cart", tags=["Cart"])


# ➕ Add item to cart
@router.post("/add/{product_id}")
def add_to_cart(product_id: int, user=Depends(get_user), db: Session = Depends(get_db)):
    user_id = user.id 

    product = db.query(Product).get(product_id)
    if not product:
        raise HTTPException(404, "Product not found")

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart:
        cart = Cart(user_id=user.id, total_price=0)
        db.add(cart)
        db.commit()
        db.refresh(cart)

    item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == product_id
    ).first()

    if item:
        item.quantity += 1
    else:
        item = CartItem(cart_id=cart.id, product_id=product_id, quantity=1)
        db.add(item)

    db.commit()
    return {"message": "Added to cart"}


# 🛒 Get My Cart
@router.get("")
def get_cart(user=Depends(get_user), db: Session = Depends(get_db)):
    user_id = user.id 

    cart = db.query(Cart).filter(Cart.user_id == user.id).first()
    if not cart or not cart.items:
        return {"cart_id": None, "items": [], "total_price": 0}

    items = [
        {
            "id": i.id,
            "quantity": i.quantity,
            "product": {
                "id": i.product.id,
                "name": i.product.name,
                "price": i.product.price,
                "image_url": i.product.image_url or ""
            }
        }
        for i in cart.items
    ]

    total_price = sum(i.quantity * i.product.price for i in cart.items)

    return {"cart_id": cart.id, "items": items, "total_price": total_price}


# 🔼 Change Quantity
@router.patch("/update/{item_id}")
def update_quantity(item_id: int, qty: int, user=Depends(get_user), db: Session = Depends(get_db)):
    user_id = user.id

    item = db.query(CcartItem).join(Cart).filter(
        Cart.user_id == user.id,
        CartItem.id == item_id
    ).first()

    if not item:
        raise HTTPException(404, "Cart item not found")

    item.quantity = qty
    db.commit()
    return {"message": "updated"}


# ❌ Remove Item
@router.delete("/remove/{item_id}")
def remove_item(item_id: int, user=Depends(get_user), db: Session = Depends(get_db)):
    user_id = user.id 

    item = db.query(CartItem).join(Cart).filter(
        Cart.user_id == user.id,
        CartItem.id == item_id
    ).first()

    if not item:
        raise HTTPException(404, "Item not found")

    db.delete(item)
    db.commit()
    return {"message": "removed"}

