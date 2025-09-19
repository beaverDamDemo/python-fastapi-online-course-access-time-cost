from pydantic import BaseModel


class InvoiceCreate(BaseModel):
    student_id: int
    koncni_znesek: float


class InvoiceOut(BaseModel):
    id: int
    student_id: int
    koncni_znesek: float

    class Config:
        orm_mode = True
