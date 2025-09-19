import tempfile

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from sqlalchemy.orm import Session

from weasyprint import HTML

from auth.dependencies import require_login
from database_main import SessionLocal
from models.invoices_model import Invoice
from models.students_model import Student
from models.inserted_data_model import InsertedData
from schemas.invoice_schema import InvoiceCreate, InvoiceOut


router = APIRouter(
    prefix="/invoices", tags=["Računi"], dependencies=[Depends(require_login)]
)

templates = Jinja2Templates(directory="templates")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Create
@router.post("/", response_model=InvoiceOut)
def create_racun(racun: InvoiceCreate, db: Session = Depends(get_db)):
    new_racun = Invoice(**racun.dict())
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)
    return new_racun


# Read all
@router.get("/", response_model=list[InvoiceOut])
def read_all_invoices(db: Session = Depends(get_db)):
    return db.query(Invoice).all()


@router.get("/find_student", response_class=HTMLResponse)
def search_student(request: Request, search_name: str, db: Session = Depends(get_db)):
    results = (
        db.query(Student)
        .filter(
            (Student.firstname.ilike(f"%{search_name}%"))
            | (Student.lastname.ilike(f"%{search_name}%"))
        )
        .all()
    )

    return templates.TemplateResponse(
        "create_invoice.html",  # or whatever your template is called
        {"request": request, "search_results": results},
    )


@router.post("/create_invoice", response_class=HTMLResponse)
def handle_form(
    request: Request, student_id: int = Form(...), db: Session = Depends(get_db)
):
    rows = db.query(InsertedData).filter(InsertedData.student_id == student_id).all()

    if not rows:
        result = {"message": f"No data found for student_id {student_id}"}
        return templates.TemplateResponse(
            "create_invoice.html", {"request": request, "result": result}
        )

    koncni_znesek = 0
    invalid_found = False

    for row in rows:
        try:
            poraba = float(row.poraba)
            cena = float(row.dinamicne_cene)
            koncni_znesek += poraba * cena
        except (ValueError, TypeError):
            invalid_found = True

    if invalid_found:
        print("❌ At least one row has invalid data format.")

    new_racun = Invoice(student_id=student_id, koncni_znesek=koncni_znesek)
    db.add(new_racun)
    db.commit()
    db.refresh(new_racun)

    result = {
        "message": "Račun ustvarjen uspešno",
        "student_id": student_id,
        "koncni_znesek": koncni_znesek,
    }
    return templates.TemplateResponse(
        "create_invoice.html", {"request": request, "result": result}
    )


@router.get("/{racun_id}", response_model=InvoiceOut)
def read_racun(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Invoice).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")
    return racun


@router.get("/{racun_id}/view_invoice", response_class=HTMLResponse)
def view_racun(request: Request, racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Invoice).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    # Get linked student info
    student = db.query(Student).filter_by(student_id=racun.student_id).first()

    return templates.TemplateResponse(
        "view_invoice.html", {"request": request, "racun": racun, "student": student}
    )


@router.post("/{racun_id}/delete")
def delete_racun_web(racun_id: int, db: Session = Depends(get_db)):
    print("Deleting racun with ID:", racun_id)
    racun = db.query(Invoice).get(racun_id)
    if racun:
        db.delete(racun)
        db.commit()
    return RedirectResponse(url="/manage_invoices", status_code=303)


@router.get("/{racun_id}/pdf")
def export_racun_pdf(racun_id: int, db: Session = Depends(get_db)):
    racun = db.query(Invoice).get(racun_id)
    if not racun:
        raise HTTPException(status_code=404, detail="Račun not found")

    student = db.query(Student).filter_by(student_id=racun.student_id).first()

    # Render the PDF-specific template (no url_for)
    html_content = templates.get_template("view_invoice_pdf.html").render(
        racun=racun, student=student
    )

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        HTML(string=html_content, base_url=".").write_pdf(tmp_file.name)
        pdf_path = tmp_file.name

    filename = f"racun_{racun.id}.pdf"
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)
