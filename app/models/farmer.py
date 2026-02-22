from sqlalchemy import Column, Integer, String, Date, Float, Enum, ForeignKey, event
from sqlalchemy.orm import relationship, Session
from app.db.session import Base
from app.models.user import User
import enum

class FarmStatus(str, enum.Enum):
    PENDING = "pending"
    VERIFIED = "verified"

class FarmerStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    DENIED = "denied"

class Farmer(Base):
    __tablename__ = "farmers"

    id = Column(Integer, primary_key=True, index=True)
    farmer_id = Column(String, unique=True, index=True) # E.g., BFD-23451
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    full_name = Column(String, index=True)
    nin = Column(String, unique=True, index=True)
    email = Column(String, index=True)
    dob = Column(Date)
    gender = Column(String)
    phone_number = Column(String)
    image_url = Column(String, nullable=True)
    
    personal_address = Column(String)
    personal_state = Column(String)
    personal_lga = Column(String)
    
    farm_address = Column(String)
    farm_state = Column(String)
    farm_lga = Column(String)
    farm_size = Column(Float)
    
    crop_type = Column(String)
    livestock_type = Column(String)
    
    farm_status = Column(Enum(FarmStatus), default=FarmStatus.PENDING)
    farmer_status = Column(Enum(FarmerStatus), default=FarmerStatus.PENDING)

    user = relationship("User", back_populates="farmer_profile")

@event.listens_for(Farmer, 'after_delete')
def delete_user_after_farmer_delete(mapper, connection, target):
    session = Session(bind=connection)
    session.query(User).filter(User.id == target.user_id).delete()
    session.close()
