import sys
import os

# Ensure the app module can be found
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.db.session import SessionLocal
from app.models.farmer import Farmer
from app.models.user import User, UserRole
from app.core.security import get_password_hash

def verify_logic():
    db = SessionLocal()
    
    # 1. Create a mock User/Farmer via the logic we implemented
    print("Testing Creation Logic...")
    test_nin = "VERIFY_TEST_NIN_123"
    
    # Clean up first if existed
    existing_farmer = db.query(Farmer).filter(Farmer.nin == test_nin).first()
    if existing_farmer:
        db.delete(existing_farmer)
        db.commit()

    user = User(
        name="Verification Test User",
        nin=test_nin,
        email="verify@test.com",
        phone_number="0000000000",
        hashed_password=get_password_hash("password"),
        role=UserRole.FARMER
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    last_farmer = db.query(Farmer).order_by(Farmer.id.desc()).first()
    next_id_num = last_farmer.id + 1 if last_farmer else 1
    generated_farmer_id = f"BFD-{next_id_num:05d}"

    farmer = Farmer(
        user_id=user.id,
        farmer_id=generated_farmer_id,
        full_name=user.name,
        nin=test_nin,
        email=user.email,
        phone_number=user.phone_number,
        personal_address="",
        personal_state="",
        personal_lga="",
        farm_address="",
        farm_state="",
        farm_lga="",
        farm_size=0,
        crop_type="",
        livestock_type=""
    )
    db.add(farmer)
    db.commit()
    db.refresh(farmer)
    
    print(f"Created Farmer with DB ID: {farmer.id}, Farmer ID: {farmer.farmer_id}")
    assert farmer.farmer_id.startswith("BFD-"), "Farmer ID prefix is incorrect!"
    assert len(farmer.farmer_id) == 9, "Farmer ID length is incorrect!"
    
    farmer_db_id = farmer.id
    user_db_id = user.id

    # 2. Test Cascade Deletion
    print("\nTesting Deletion Cascade...")
    db.delete(farmer)
    db.commit()
    
    deleted_farmer = db.query(Farmer).filter(Farmer.id == farmer_db_id).first()
    deleted_user = db.query(User).filter(User.id == user_db_id).first()
    
    print(f"Farmer after delete (expected None): {deleted_farmer}")
    print(f"User after farmer delete (expected None): {deleted_user}")
    
    assert deleted_farmer is None, "Farmer was not deleted!"
    assert deleted_user is None, "User was NOT cascade deleted! Event hook failed."
    
    print("\nVerification Successful! All tests passed.")

    db.close()

if __name__ == "__main__":
    verify_logic()
