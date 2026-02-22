from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
import io
from app.db.session import get_db
from app.models.farmer import Farmer
from app.models.user import User, UserRole
from app.schemas.farmer import FarmerCreate, FarmerOut, FarmerUpdate
from app.api.dependencies import get_current_active_admin
from app.core.security import get_password_hash

router = APIRouter()

@router.post("/", response_model=FarmerOut)
def create_farmer(
    farmer_in: FarmerCreate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    # Check if NIN already exists
    if db.query(Farmer).filter(Farmer.nin == farmer_in.nin).first():
        raise HTTPException(status_code=400, detail="Farmer with this NIN already exists")
    
    # 1. Create User entry (auto-populate)
    user = User(
        name=farmer_in.full_name,
        nin=farmer_in.nin,
        email=farmer_in.email,
        phone_number=farmer_in.phone_number,
        hashed_password=get_password_hash(farmer_in.nin), # Password is NIN
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Generate BFD Farmer ID
    last_farmer = db.query(Farmer).order_by(Farmer.id.desc()).first()
    next_id_num = last_farmer.id + 1 if last_farmer else 1
    generated_farmer_id = f"BFD-{next_id_num:05d}"
    
    # 2. Create Farmer entry
    farmer = Farmer(**farmer_in.dict(), user_id=user.id, farmer_id=generated_farmer_id)
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    return farmer

@router.get("/", response_model=List[FarmerOut])
def read_farmers(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    farmers = db.query(Farmer).offset(skip).limit(limit).all()
    return farmers

@router.get("/{farmer_id}", response_model=FarmerOut)
def read_farmer(
    farmer_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    return farmer

@router.put("/{farmer_id}", response_model=FarmerOut)
def update_farmer(
    farmer_id: int,
    farmer_in: FarmerUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    update_data = farmer_in.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(farmer, field, value)
    
    # Update related User if name/nin/phone/email changed
    if any(k in update_data for k in ["full_name", "nin", "phone_number", "email"]):
        user = db.query(User).filter(User.id == farmer.user_id).first()
        if user:
            if "full_name" in update_data: user.name = update_data["full_name"]
            if "nin" in update_data: 
                user.nin = update_data["nin"]
                user.hashed_password = get_password_hash(update_data["nin"]) # Update password if NIN changes
            if "phone_number" in update_data: user.phone_number = update_data["phone_number"]
            if "email" in update_data: user.email = update_data["email"]
    
    db.commit()
    db.refresh(farmer)
    return farmer

@router.delete("/{farmer_id}")
def delete_farmer(
    farmer_id: int,
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    farmer = db.query(Farmer).filter(Farmer.id == farmer_id).first()
    if not farmer:
        raise HTTPException(status_code=404, detail="Farmer not found")
    
    # Delete associated user as well? Usually yes if auto-populated
    user = db.query(User).filter(User.id == farmer.user_id).first()
    db.delete(farmer)
    if user:
        db.delete(user)
    db.commit()
    return {"message": "Farmer and associated user deleted successfully"}

@router.delete("/")
def delete_all_farmers(
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    # This is destructive!
    db.query(Farmer).delete()
    db.query(User).filter(User.role == UserRole.FARMER).delete()
    db.commit()
    return {"message": "All farmers and their user accounts deleted"}

@router.post("/upload")
async def upload_farmers(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    admin: User = Depends(get_current_active_admin)
):
    contents = await file.read()
    if file.filename.endswith('.csv'):
        df = pd.read_csv(io.StringIO(contents.decode('base64' if 'base64' in contents else 'utf-8'))) # Simplified
    elif file.filename.endswith(('.xlsx', '.xls')):
        df = pd.read_excel(io.BytesIO(contents))
    else:
        raise HTTPException(status_code=400, detail="Invalid file format")
    
    # For now, let's assume simple CSV processing
    try:
        df = pd.read_csv(io.StringIO(contents.decode('utf-8'))) if file.filename.endswith('.csv') else pd.read_excel(io.BytesIO(contents))
        
        count = 0
        
        # Get the current highest ID before processing the batch to ensure sequential IDs
        last_farmer = db.query(Farmer).order_by(Farmer.id.desc()).first()
        next_id_num = last_farmer.id + 1 if last_farmer else 1
        
        for _, row in df.iterrows():
            # Check if NIN already exists
            if db.query(User).filter(User.nin == str(row['nin'])).first():
                continue
            
            user = User(
                name=row['full_name'],
                nin=str(row['nin']),
                email=row['email'],
                phone_number=str(row['phone_number']),
                hashed_password=get_password_hash(str(row['nin'])), # Password is NIN
                role=UserRole.FARMER
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            
            generated_farmer_id = f"BFD-{next_id_num:05d}"
            
            farmer = Farmer(
                farmer_id=generated_farmer_id,
                user_id=user.id,
                full_name=row['full_name'],
                nin=str(row['nin']),
                email=row['email'],
                # ... other fields would need to be in the CSV
                phone_number=str(row['phone_number']),
                personal_address=row.get('personal_address', ''),
                personal_state=row.get('personal_state', ''),
                personal_lga=row.get('personal_lga', ''),
                farm_address=row.get('farm_address', ''),
                farm_state=row.get('farm_state', ''),
                farm_lga=row.get('farm_lga', ''),
                farm_size=float(row.get('farm_size', 0)),
                crop_type=row.get('crop_type', ''),
                livestock_type=row.get('livestock_type', ''),
            )
            db.add(farmer)
            count += 1
            next_id_num += 1 # Increment for the next iteration
        
        db.commit()
        return {"message": f"Successfully uploaded {count} farmers"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing file: {str(e)}")
