# app/api/v1/endpoints/auth.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import User
from app.schemas.auth import UserLogin, UserResponse
from app.api.core.dependencies import create_access_token # From core/dependencies.py

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/login", response_model=UserResponse)
async def login_for_access_token(request: UserLogin, db: Session = Depends(get_db)):
    # 1. Authenticate (LOOKUP USER)
    user = db.query(User).filter(User.username == request.email).first()

    # MOCK PASSWORD CHECK: This MUST be replaced with bcrypt/argon2 hashing comparison in production.
    if not user or user.password_hash != request.password: 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
        )
    
    if user.status != 'active':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Account status is '{user.status}'. Please contact the Commissioner.",
        )

    # 2. Create Token payload (Crucial for RBAC)
    access_token = create_access_token(data={"user_id": user.user_id, "role": user.role})

    # 3. Return response with token and core user data
    return UserResponse(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        department_id=user.department_id,
        token=access_token
    )

@router.post("/signup")
async def register_user(request: UserLogin, db: Session = Depends(get_db)):
    # Implementation for signup (saves user in 'pending' status)
    if db.query(User).filter(User.username == request.email).first():
        raise HTTPException(status_code=400, detail="User already exists.")

    new_user = User(
        username=request.email,
        password_hash=request.password, # MOCK HASH - Secure this later!
        role="employee", # Default signup role is 'employee'
        status="pending", 
        department_id=1 # MOCK: Assign to an existing department ID
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "Signup request sent. Your account is pending Commissioner approval."}