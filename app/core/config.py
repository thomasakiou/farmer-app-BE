import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    PROJECT_NAME: str = "Farmer Data Capture"
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:ebimobowei81@localhost/farmer_db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "yoursecretkeyhere")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        case_sensitive = True

settings = Settings()
