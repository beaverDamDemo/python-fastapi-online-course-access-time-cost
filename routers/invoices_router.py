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
    prefix="/invoices", tags=["Invoices"], dependencies=[Depends(require_login)]
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
def create_invoice(invoice: InvoiceCreate, db: Session = Depends(get_db)):
    new_invoice = Invoice(**invoice.dict())
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return new_invoice


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

    total = 0
    invalid_found = False

    for row in rows:
        try:
            poraba = float(row.poraba)
            cena = float(row.dinamicne_cene)
            total += poraba * cena
        except (ValueError, TypeError):
            invalid_found = True

    if invalid_found:
        print("❌ At least one row has invalid data format.")

    new_invoice = Invoice(student_id=student_id, total=total)
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)

    result = {
        "message": "Invoice ustvarjen uspešno",
        "student_id": student_id,
        "total": total,
    }
    return templates.TemplateResponse(
        "create_invoice.html", {"request": request, "result": result}
    )


@router.get("/{invoice_id}", response_model=InvoiceOut)
def read_invoice(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    return invoice


@router.get("/{invoice_id}/view_invoice", response_class=HTMLResponse)
def view_invoice(request: Request, invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    # Get linked student info
    student = db.query(Student).filter_by(student_id=invoice.student_id).first()

    return templates.TemplateResponse(
        "view_invoice.html", {"request": request, "invoice": invoice, "student": student}
    )


@router.post("/{invoice_id}/delete")
def delete_invoice_web(invoice_id: int, db: Session = Depends(get_db)):
    print("Deleting invoice with ID:", invoice_id)
    invoice = db.query(Invoice).get(invoice_id)
    if invoice:
        db.delete(invoice)
        db.commit()
    return RedirectResponse(url="/manage_invoices", status_code=303)


@router.get("/{invoice_id}/pdf")
def export_invoice_pdf(invoice_id: int, db: Session = Depends(get_db)):
    invoice = db.query(Invoice).get(invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")

    student = db.query(Student).filter_by(student_id=invoice.student_id).first()

    # Render the PDF-specific template (no url_for)
    html_content = templates.get_template("view_invoice_pdf.html").render(
        invoice=invoice, student=student
    )

    # Generate PDF
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        HTML(string=html_content, base_url=".").write_pdf(tmp_file.name)
        pdf_path = tmp_file.name

    filename = f"invoice_{invoice.id}.pdf"
    return FileResponse(pdf_path, media_type="application/pdf", filename=filename)
