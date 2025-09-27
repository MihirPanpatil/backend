# app/api/core/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    # Config tells Pydantic to load from .env file
    model_config = SettingsConfigDict(env_file='.env', extra='ignore')

    # --- Database Settings (PostgreSQL) ---
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str
    
    @property
    def DATABASE_URL(self) -> str:
        # Uses the app_rw user
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    # --- AWS & S3 Settings ---
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    S3_RAW_BUCKET: str
    S3_VERIFIED_BUCKET: str

    # --- IPFS Settings ---
    IPFS_API_URL: str
    
    # --- JWT Authentication Settings ---
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    # --- CORS Configuration (Update this with your Vercel URL) ---
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "https://*.vercel.app", 
        "https://pmc.cityvault.in",
    ]

settings = Settings()