from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    student_id: int
    total: float


class InvoiceOut(BaseModel):
    id: int
    student_id: int
    total: float

    class Config:
        orm_mode = True
