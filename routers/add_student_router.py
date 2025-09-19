from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from auth.dependencies import require_login
from database_main import SessionLocal
from models.students_model import Student


router = APIRouter(dependencies=[Depends(require_login)])
templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/add_student", response_class=HTMLResponse)
def show_add_student(request: Request):
    return templates.TemplateResponse("add_student.html", {"request": request})


@router.post("/add_student", response_class=HTMLResponse)
def handle_add_student(
    request: Request,
    firstname: str = Form(...),
    lastname: str = Form(...),
    address: str = Form(...),
    db: Session = Depends(get_db),
):
    new_student = Student(firstname=firstname, lastname=lastname, address=address)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    result = {
        "message": "Student successfully added!",
        "student_id": new_student.student_id,
        "firstname": new_student.firstname,
        "lastname": new_student.lastname,
        "address": new_student.address,
    }
    return templates.TemplateResponse(
        "add_student.html", {"request": request, "result": result}
    )


@router.get("/manage_students", response_class=HTMLResponse)
def manage_students(request: Request):
    db = SessionLocal()
    students = db.query(Student).all()
    db.close()
    return templates.TemplateResponse(
        "manage_students.html", {"request": request, "students": students}
    )
