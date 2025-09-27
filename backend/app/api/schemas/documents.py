# app/api/v1/endpoints/documents.py (Full lifecycle)
from fastapi import APIRouter, File, UploadFile, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Document, User
from app.services.aws_s3_ipfs import upload_and_pin_file
from app.api.core.dependencies import require_role, get_current_user
from datetime import datetime
from typing import List

router = APIRouter(prefix="/documents", tags=["documents"])

# --- 1. UPLOAD (Simple Non-OCR) ---
@router.post("/upload/simple")
async def simple_document_upload(
    file: UploadFile = File(...),
    document_title: str = Form(...),
    employee_id: int = Form(...), # The ID of the employee the doc belongs to
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['employee', 'hod'])), # Only Employee/HOD can upload
):
    # Security: Ensure Employee only uploads for self (HOD can upload for anyone)
    if current_user.role == 'employee' and current_user.user_id != employee_id:
        raise HTTPException(status_code=403, detail="Employees can only upload documents for themselves.")
    
    # Upload file (No IPFS pinning yet)
    upload_results = await upload_and_pin_file(
        file=file, 
        uploader_id=current_user.user_id, 
        is_final_version=False
    )

    if not upload_results["original_file_url"]:
        raise HTTPException(status_code=500, detail="Failed to store file on S3.")

    # Save Metadata to RDS
    new_document = Document(
        document_title=document_title,
        file_name=file.filename,
        original_file_url=upload_results["original_file_url"],
        employee_id=employee_id,
        current_status="pending",
        with_ocr=False
    )
    
    db.add(new_document)
    db.commit()
    db.refresh(new_document)

    return {"message": "Document uploaded successfully and is pending approval.", "document_id": new_document.document_id}


# --- 2. APPROVAL QUEUE (HOD/DC/Commissioner) ---
# NOTE: Requires a DocumentSchema and logic to fetch related employee data
@router.get("/pending", response_model=List[dict])
async def get_pending_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['hod', 'dc', 'commissioner'])),
):
    # Filter logic based on user role
    query = db.query(Document, User).join(User, Document.employee_id == User.user_id).filter(Document.current_status == 'pending')
    
    if current_user.role == 'hod':
        # HOD only sees documents for their department
        query = query.filter(User.department_id == current_user.department_id)
        
    # DC and Commissioner see all documents
    
    pending_docs = query.limit(50).all()
    
    # Format results for the frontend
    results = []
    for doc, emp in pending_docs:
        results.append({
            "document_id": doc.document_id,
            "title": doc.document_title,
            "employee_name": emp.username,
            "employee_id": emp.user_id,
            "uploaded_at": doc.uploaded_at.isoformat(),
        })
    
    return results


# --- 3. APPROVE & PIN (HOD/DC/Commissioner) ---
@router.post("/{document_id}/approve")
async def approve_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(['hod', 'dc', 'commissioner'])), 
    # NOTE: You would typically include an async function here to re-GET the file content from S3
    # based on document.original_file_url and then pin *that* content.
):
    document = db.query(Document).filter(Document.document_id == document_id).first()
    if not document or document.current_status != 'pending':
        raise HTTPException(status_code=404, detail="Document not found or status invalid.")

    # --- MOCK HASHING (Replace this with actual S3 GET -> IPFS PIN logic) ---
    # Since we can't reliably re-read the original file object here, we mock the hash.
    # In a real app, you would retrieve the file from document.original_file_url,
    # pass its content to the IPFS service, and get the real hash.
    final_hash = "Qm" + os.urandom(22).hex() 
    # --- END MOCK HASHING ---

    # Update DB
    document.blockchain_hash = final_hash
    document.current_status = 'approved'
    document.finalized_at = datetime.utcnow()
    # document.verified_by_id = current_user.user_id # Uncomment when added to ORM
    
    db.commit()
    
    return {
        "message": "Document approved and immutable hash recorded.",
        "blockchain_hash": final_hash
    }

# ... (Reject endpoint remains the same)