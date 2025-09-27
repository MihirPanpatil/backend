# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey, func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
# ... (User and Department models as derived previously)
class Department(Base):
    __tablename__ = "departments"
    department_id = Column(Integer, primary_key=True, index=True)
    department_name = Column(String(100), nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), default=func.now())
    users = relationship("User", back_populates="department")

class User(Base):
    __tablename__ = "users"
    user_id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), nullable=False, unique=True) # Used for login email
    password_hash = Column(String, nullable=False)
    role = Column(String(50), nullable=False) # Roles: 'employee', 'hod', 'dc', 'commissioner'
    department_id = Column(Integer, ForeignKey('departments.department_id'))
    status = Column(String(20), default='pending') # Status: 'active', 'pending', 'rejected'
    created_at = Column(DateTime(timezone=True), default=func.now())
    department = relationship("Department", back_populates="users")
    documents = relationship("Document", back_populates="employee")

class Document(Base):
    __tablename__ = "documents"
    document_id = Column(Integer, primary_key=True, index=True)
    employee_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    original_file_url = Column(String, nullable=False) # S3 key/path
    merged_file_url = Column(String)                   # S3 key/path (Skipped for now)
    with_ocr = Column(Boolean, default=False)
    blockchain_hash = Column(String(64))
    current_status = Column(String(20), default='pending') # Status: 'pending', 'approved', 'rejected'
    uploaded_at = Column(DateTime(timezone=True), default=func.now())
    finalized_at = Column(DateTime(timezone=True))
    employee = relationship("User", back_populates="documents")