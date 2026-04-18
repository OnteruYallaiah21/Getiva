from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, UserRole, Student, Recruiter
from ..storage import storage_client
from .auth import get_current_user, require_role

router = APIRouter(prefix="/api/files", tags=["files"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {".pdf", ".doc", ".docx", ".txt"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Upload a resume file to Supabase storage."""
    # Validate file extension
    file_ext = "." + file.filename.split(".")[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"File type not allowed. Allowed: {', '.join(ALLOWED_EXTENSIONS)}")

    # Read file
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")

    try:
        # Get student ID
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student:
                raise HTTPException(status_code=404, detail="Student profile not found")
            student_id = str(student.id)
        else:
            # For recruiter/admin, use user ID or provided student ID
            student_id = str(current_user.id)

        # Upload to Supabase
        file_url = storage_client.upload_file(content, file.filename, student_id)

        # Update student resume URL if this is a student
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            student.resume_url = file_url
            db.commit()

        return {
            "filename": file.filename,
            "url": file_url,
            "size": len(content),
            "message": "Resume uploaded successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/resume")
async def get_resume(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Get current student's resume URL."""
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        return {"resume_url": student.resume_url}

    raise HTTPException(status_code=403, detail="Only students can retrieve their resume")


@router.delete("/resume/{file_path}")
async def delete_file(
    file_path: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN)),
):
    """Delete a file from storage."""
    try:
        # For security, only allow students to delete their own files or admins to delete any
        if current_user.role == UserRole.STUDENT:
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student or str(student.id) not in file_path:
                raise HTTPException(status_code=403, detail="Cannot delete other user's files")

        storage_client.delete_file(file_path)

        return {"message": "File deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Deletion failed: {str(e)}")


@router.get("/list")
async def list_files(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.ADMIN)),
):
    """List all files for current student."""
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        if not student:
            raise HTTPException(status_code=404, detail="Student profile not found")

        files = storage_client.list_files(str(student.id))
        return {"files": files}

    raise HTTPException(status_code=403, detail="Only students can list their files")
