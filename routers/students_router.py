from fastapi import APIRouter, Depends, HTTPException, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from auth.dependencies import require_login
from database_main import SessionLocal
from models.students_model import Student
from schemas.students_schema import StudentCreate, StudentOut, StudentUpdate

templates = Jinja2Templates(directory="templates")

router = APIRouter(
    prefix="/students", tags=["Students"], dependencies=[Depends(require_login)]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/{student_id}/uredi", response_class=HTMLResponse)
def edit_student_form(student_id: int, request: Request, db: Session = Depends(get_db)):
    print(f"Edit route hit for student_id={student_id}")
    student = db.query(Student).get(student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return templates.TemplateResponse(
        "edit_student.html", {"request": request, "student": student}
    )


@router.post("/{student_id}/uredi")
def edit_student_submit(
    student_id: int,
    firstname: str = Form(...),
    lastname: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    student = db.query(Student).get(student_id)
    student.firstname = firstname
    student.lastname = lastname
    student.address = address
    db.commit()
    return RedirectResponse(url="/manage_students", status_code=303)


@router.post("/{student_id}/delete")
def delete_student_form(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(student_id=student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return RedirectResponse(url="/manage_students", status_code=303)


@router.post("/", response_model=StudentOut)
def create_student(student: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(**student.dict())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/", response_model=list[StudentOut])
def read_all_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@router.get("/{student_id}", response_model=StudentOut)
def read_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(student_id=student_id).first()
    if not student:
        raise HTTPException(
            status_code=404, detail="Student with ID {student_id} not found"
        )
    return student


@router.put("/{student_id}", response_model=StudentOut)
def update_student(
    student_id: int, update: StudentUpdate, db: Session = Depends(get_db)
):
    student = db.query(Student).filter_by(student_id=student_id).first()
    if not student:
        raise HTTPException(
            status_code=404, detail="Student with ID {student_id} not found"
        )
    for key, value in update.dict().items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    student = db.query(Student).filter_by(student_id=student_id).first()
    if not student:
        raise HTTPException(
            status_code=404, detail="Student with ID {student_id} not found"
        )
    db.delete(student)
    db.commit()
    return {"message": f"Student {student_id} deleted"}
