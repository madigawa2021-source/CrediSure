from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from sqlalchemy.orm import Session
from uuid import uuid4
from database.connection import get_db
from models.models import User, UploadedDocument
from schemas.schemas import UploadResponse
from utils.auth import get_current_user

router = APIRouter(prefix="/upload", tags=["File Upload"])


@router.post("/upload-statement", response_model=UploadResponse)
def upload_statement(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed"
        )
    s3_key = f"{uuid4()}-{file.filename}"
    
    # TODO: replace with boto3 S3 upload
    
    new_document = UploadedDocument(
        user_id=current_user.id,
        file_name=file.filename,
        s3_key=s3_key,
        file_type="pdf",
        status="completed"
    )
    db.add(new_document)
    db.commit()
    db.refresh(new_document)
    return {
        "file_name": file.filename,
        "file_type": "pdf",
        "status": "completed",
        "message": "Statement uploaded successfully",
        "uploaded_at": str(new_document.uploaded_at),
        "next_step": "Go to AI Analysis to analyze this statement"
    }
