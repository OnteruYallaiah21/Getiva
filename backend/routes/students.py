from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Student, User, UserRole
from ..schemas import StudentDirectoryEntry
from .auth import require_role

router = APIRouter(prefix="/api/students", tags=["students"])


@router.get("", response_model=List[StudentDirectoryEntry])
def list_students_directory(
    db: Session = Depends(get_db),
    _: User = Depends(require_role(UserRole.RECRUITER, UserRole.ADMIN)),
):
    """List all students (for recruiter application assignment). Includes login username and profile name."""
    students = (
        db.query(Student)
        .join(User, Student.user_id == User.id)
        .filter(User.role == UserRole.STUDENT, User.is_active == 1)
        .order_by(Student.full_name.asc(), User.username.asc())
        .all()
    )
    return [
        StudentDirectoryEntry(
            id=s.id,
            username=s.user.username,
            full_name=s.full_name,
            email=s.user.email,
        )
        for s in students
    ]
