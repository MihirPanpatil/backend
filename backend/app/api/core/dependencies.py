# app/api/core/dependencies.py
from fastapi import Header, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from datetime import datetime, timedelta
from app.core.config import settings
from app.db.database import get_db
from sqlalchemy.orm import Session
from app.db.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_jwt_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token.")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    payload = decode_jwt_token(token)
    user_id = payload.get("user_id") 

    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token payload missing user identifier.")
    
    # Fetch the user from RDS
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user or user.status != 'active':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User inactive or not found.")
        
    return user

def require_role(required_roles: list):
    """Dependency factory for Role-Based Access Control."""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in required_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Role '{current_user.role}' is not authorized."
            )
        return current_user
    return role_checker