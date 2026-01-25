from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import date

from app.database import get_db
from app.models import Order
from app.auth.utils import admin_required

router = APIRouter(prefix="/admin/dashboard", tags=["Admin Dashboard"])


@router.get("/stats")
def dashboard_stats(db: Session = Depends(get_db), _=Depends(admin_required)):
    orders = db.query(Order).all()

    total_revenue = sum(o.total_price for o in orders)
    total_orders = len(orders)

    today = date.today()

    today_orders = [
        o for o in orders if o.created_at.date() == today
    ]

    today_revenue = sum(o.total_price for o in today_orders)

    pending_orders = len([o for o in orders if o.status == "Pending"])

    return {
        "total_revenue": total_revenue,
        "total_orders": total_orders,
        "today_revenue": today_revenue,
        "pending_orders": pending_orders,
    }

