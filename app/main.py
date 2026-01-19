from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Ensure models are loaded
from app import models

app = FastAPI(title="Primerice API")

# Routers
from app.auth.routes import router as auth_router
from app.products.public_routes import router as public_products_router
from app.products.admin_routes import router as admin_products_router
from app.orders.routes import router as orders_router
from app.cart.routes import router as cart_router
from app.addresses.routes import router as addresses_router
from app.admin.user_routes import router as admin_users_router



# --------------------
# CORS
# --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# Static files
# --------------------
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# --------------------
# Health check (IMPORTANT)
# --------------------
@app.get("/health")
def health():
    return {"status": "ok"}

# --------------------
# Root
# --------------------
@app.get("/")
def home():
    return {"status": "Primerice backend running"}

# --------------------
# Register routers
# --------------------
app.include_router(auth_router)
app.include_router(public_products_router)
app.include_router(admin_products_router)
app.include_router(orders_router)
app.include_router(cart_router)
app.include_router(addresses_router)
app.include_router(admin_users_router)


