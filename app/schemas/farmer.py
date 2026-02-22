from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional, List
from app.models.user import UserRole
from app.models.farmer import FarmStatus, FarmerStatus

# User Schemas
class UserBase(BaseModel):
    name: str
    nin: str
    phone_number: str
    role: UserRole = UserRole.FARMER

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    name: Optional[str] = None
    phone_number: Optional[str] = None
    password: Optional[str] = None

class UserOut(UserBase):
    id: int

    class Config:
        from_attributes = True

# Farmer Schemas
class FarmerBase(BaseModel):
    full_name: str
    nin: str
    email: EmailStr
    dob: date
    gender: str
    phone_number: str
    image_url: Optional[str] = None
    
    personal_address: str
    personal_state: str
    personal_lga: str
    
    farm_address: str
    farm_state: str
    farm_lga: str
    farm_size: float
    
    crop_type: str
    livestock_type: str
    
    farm_status: FarmStatus = FarmStatus.PENDING
    farmer_status: FarmerStatus = FarmerStatus.PENDING

class FarmerCreate(FarmerBase):
    pass

class FarmerUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    dob: Optional[date] = None
    gender: Optional[str] = None
    phone_number: Optional[str] = None
    image_url: Optional[str] = None
    
    personal_address: Optional[str] = None
    personal_state: Optional[str] = None
    personal_lga: Optional[str] = None
    
    farm_address: Optional[str] = None
    farm_state: Optional[str] = None
    farm_lga: Optional[str] = None
    farm_size: Optional[float] = None
    
    crop_type: Optional[str] = None
    livestock_type: Optional[str] = None
    
    farm_status: Optional[FarmStatus] = None
    farmer_status: Optional[FarmerStatus] = None

class FarmerOut(FarmerBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True

# Auth Schemas
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    nin: Optional[str] = None
    role: Optional[str] = None

class LoginRequest(BaseModel):
    nin: str
    password: Optional[str] = "password" # Default password for farmers if needed, or specific for admin
