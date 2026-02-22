from app.db.session import SessionLocal
from app.db.base import User # This ensures all models are imported
from app.models.user import UserRole
from app.core.security import get_password_hash

def seed_admin():
    db = SessionLocal()
    admin_nin = "1234567890"
    admin_user = db.query(User).filter(User.nin == admin_nin).first()
    
    if not admin_user:
        admin_user = User(
            name="Admin User",
            nin=admin_nin,
            email="admin@farmer.com",
            phone_number="08012345678",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN
        )
        db.add(admin_user)
        db.commit()
        print(f"Admin user created with NIN: {admin_nin} and password: admin123")
    else:
        print("Admin user already exists.")
    db.close()

if __name__ == "__main__":
    seed_admin()
