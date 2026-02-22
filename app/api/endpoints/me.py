from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User
from app.models.farmer import Farmer
from app.schemas.farmer import FarmerOut
from app.api.dependencies import get_current_active_farmer

router = APIRouter()

@router.get("/farmer", response_model=FarmerOut)
def get_my_farmer_data(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_farmer)
):
    farmer = db.query(Farmer).filter(Farmer.user_id == current_user.id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer profile not found")
    return farmer
