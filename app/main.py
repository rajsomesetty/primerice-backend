from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.admin.routes import router as admin_router
from app.admin.product_routes import router as admin_product_router
from app.admin.upload_routes import router as upload_router

# Import models (ensure SQLAlchemy loads them)
from app import models

app = FastAPI(title="Primerice API")  # ✔ FIRST define app

# Import Routers
from app.auth_routes import router as auth_router
from app.products.public_routes import router as public_products_router
from app.products.admin_routes import router as admin_products_router
from app.orders.routes import router as orders_router
from app.cart.routes import router as cart_router
from app.addresses.routes import router as addresses_router


# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Register Routers
app.include_router(auth_router)
app.include_router(public_products_router)
app.include_router(admin_products_router)
app.include_router(orders_router)
app.include_router(cart_router)
app.include_router(addresses_router)  # ✔ Correct position
app.include_router(admin_router)
app.include_router(admin_product_router)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
app.include_router(upload_router)

@app.get("/")
def home():
    return {"status": "Primerice backend running"}

