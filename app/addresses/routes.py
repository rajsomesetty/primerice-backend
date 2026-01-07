from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Address
from app.deps import get_current_user
from app.schemas import AddressCreate

router = APIRouter(prefix="/addresses", tags=["Addresses"])


@router.post("")
def add_address(data: AddressCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    addr = Address(
        user_id=user.id,
        name=data.name,
        mobile=data.mobile,
        address_line=data.address_line,
        city=data.city,
        pincode=data.pincode,
    )
    db.add(addr)
    db.commit()
    db.refresh(addr)
    return addr


@router.get("")
def list_addresses(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Address).filter(Address.user_id == user.id).all()


@router.delete("/{address_id}")
def delete_address(address_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    addr = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id).first()
    if not addr:
        raise HTTPException(status_code=404, detail="Address not found")

    db.delete(addr)
    db.commit()
    return {"message": "Deleted"}

