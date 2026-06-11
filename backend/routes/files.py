from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, UserRole, Student, Recruiter, StoredDocument, Application
from ..storage_fetch import fetch_bytes_from_stored_url
from ..schemas import StoredDocumentResponse
from ..file_storage_dispatch import upload_admin_document_bytes, upload_resume_bytes
from ..storage import storage_client
from .auth import get_current_user, require_role

router = APIRouter(prefix="/api/files", tags=["files"])

# Allowed file extensions (resumes / application attachments)
ALLOWED_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".txt",
    ".rtf",
    ".odt",
    ".ppt",
    ".pptx",
    ".xls",
    ".xlsx",
    ".csv",
    ".png",
    ".jpg",
    ".jpeg",
    ".gif",
    ".webp",
    ".zip",
    ".msg",
    ".eml",
}
ADMIN_DOC_EXTENSIONS = ALLOWED_EXTENSIONS
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_ADMIN_DOC_SIZE = 10 * 1024 * 1024  # 10MB for admin policy docs


def _user_can_access_application_resume(
    db: Session, current_user: User, application: Application,
) -> bool:
    if current_user.role == UserRole.ADMIN:
        return True
    if current_user.role == UserRole.STUDENT:
        student = db.query(Student).filter(Student.user_id == current_user.id).first()
        return student is not None and application.student_id == student.id
    if current_user.role == UserRole.RECRUITER:
        recruiter = db.query(Recruiter).filter(Recruiter.user_id == current_user.id).first()
        return recruiter is not None and application.recruiter_id == recruiter.id
    return False


def _resolve_application_resume_url(db: Session, application: Application) -> Optional[str]:
    url = (application.resume_url or "").strip()
    if url:
        return url
    student = db.query(Student).filter(Student.id == application.student_id).first()
    if student and student.resume_url:
        return student.resume_url.strip()
    return None


def _application_resume_response(
    db: Session,
    application: Application,
    as_download: bool,
) -> Response:
    stored_url = _resolve_application_resume_url(db, application)
    if not stored_url:
        raise HTTPException(status_code=404, detail="No resume attached to this application")
    try:
        body, filename, content_type = fetch_bytes_from_stored_url(stored_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not load resume: {e}") from e

    disposition = "attachment" if as_download else "inline"
    safe_name = filename.replace('"', "")
    headers = {"Content-Disposition": f"{disposition}; filename=\"{safe_name}\""}
    return Response(content=body, media_type=content_type, headers=headers)


@router.get("/application/{application_id}/resume/view")
def view_application_resume(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Stream application resume for in-browser viewing (auth required)."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if not _user_can_access_application_resume(db, current_user, application):
        raise HTTPException(status_code=403, detail="Not allowed to view this resume")
    return _application_resume_response(db, application, as_download=False)


@router.get("/application/{application_id}/resume/download")
def download_application_resume(
    application_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Download application resume file (auth required)."""
    application = db.query(Application).filter(Application.id == application_id).first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    if not _user_can_access_application_resume(db, current_user, application):
        raise HTTPException(status_code=403, detail="Not allowed to download this resume")
    return _application_resume_response(db, application, as_download=True)


@router.post("/resume")
async def upload_resume(
    file: UploadFile = File(...),
    student_id: Optional[UUID] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.STUDENT, UserRole.RECRUITER, UserRole.ADMIN)),
):
    """Upload a resume (server-side only).

    Uses Backblaze B2 when configured (primary for recruiter uploads); on failure falls back to Supabase.
    The browser never sees storage credentials.
    Response returns a public URL string for callers to persist (e.g. ``Student.resume_url`` or
    ``Application.resume_url`` in Postgres).

    Students upload for themselves (updates profile ``resume_url``).
    Recruiters and admins must send ``student_id`` (multipart form); the file is stored under that
    student's folder and the URL is returned for attaching to an application (profile is not updated).
    """
    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Filename must include an extension (e.g. .pdf)")
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    # Read file
    content = await file.read()

    # Validate file size
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=413, detail=f"File too large. Max size: {MAX_FILE_SIZE / 1024 / 1024}MB")

    try:
        if current_user.role == UserRole.STUDENT:
            if student_id is not None:
                raise HTTPException(status_code=400, detail="Students cannot specify student_id")
            student = db.query(Student).filter(Student.user_id == current_user.id).first()
            if not student:
                raise HTTPException(status_code=404, detail="Student profile not found")
            storage_student_id = str(student.id)
        else:
            if student_id is None:
                raise HTTPException(
                    status_code=400,
                    detail="student_id is required when uploading a resume as a recruiter or administrator",
                )
            student = db.query(Student).filter(Student.id == student_id).first()
            if not student:
                raise HTTPException(status_code=404, detail="Student not found")
            storage_student_id = str(student.id)

        file_url = upload_resume_bytes(content, file.filename, storage_student_id)

        if current_user.role == UserRole.STUDENT:
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


@router.post("/admin/documents", response_model=StoredDocumentResponse, status_code=201)
async def upload_admin_document(
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(UserRole.ADMIN)),
):
    """Upload a document (B2 first if configured, else Supabase); save public URL in Postgres. Admin only."""
    if not file.filename or "." not in file.filename:
        raise HTTPException(status_code=400, detail="Filename must include an extension (e.g. .pdf)")
    file_ext = "." + file.filename.rsplit(".", 1)[-1].lower()
    if file_ext not in ADMIN_DOC_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed: {', '.join(sorted(ADMIN_DOC_EXTENSIONS))}",
        )

    content = await file.read()
    if len(content) > MAX_ADMIN_DOC_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File too large. Max size: {MAX_ADMIN_DOC_SIZE / 1024 / 1024}MB",
        )

    try:
        url = upload_admin_document_bytes(content, file.filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    clean_title = (title or "").strip() or None
    row = StoredDocument(
        file_name=file.filename,
        title=clean_title,
        storage_url=url,
        uploaded_by_id=current_user.id,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row


@router.get("/admin/documents", response_model=List[StoredDocumentResponse])
def list_admin_documents(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.ADMIN)),
):
    """List admin-uploaded documents (metadata + Supabase URLs stored in Neon)."""
    return (
        db.query(StoredDocument)
        .order_by(StoredDocument.created_at.desc())
        .all()
    )


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
