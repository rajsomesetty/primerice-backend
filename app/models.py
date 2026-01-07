from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime


# USERS
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    mobile = Column(String, unique=True, index=True)
    password = Column(String)
    role = Column(String, default="user")

    orders = relationship("Order", back_populates="user", cascade="all, delete")
    addresses = relationship("Address", back_populates="user", cascade="all, delete")


# ADDRESSES
class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String)
    mobile = Column(String)
    address_line = Column(String)
    city = Column(String)
    pincode = Column(String)

    user = relationship("User", back_populates="addresses")


# PRODUCTS
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(Text, nullable=True)   # ✅ ADD THIS
    image_url = Column(String)

# ORDERS
class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    items_json = Column(String)
    total_price = Column(Float)
    address_id = Column(Integer, ForeignKey("addresses.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="Pending")

    user = relationship("User", back_populates="orders")
    address = relationship("Address")

# --- CART ---
class Cart(Base):
    __tablename__ = "carts"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    total_price = Column(Float, default=0.0)

    items = relationship("CartItem", back_populates="cart")


class CartItem(Base):
    __tablename__ = "cart_items"

    id = Column(Integer, primary_key=True)
    cart_id = Column(Integer, ForeignKey("carts.id"))
    product_id = Column(Integer, ForeignKey("products.id"))
    quantity = Column(Integer, default=1)

    cart = relationship("Cart", back_populates="items")
    product = relationship("Product")

