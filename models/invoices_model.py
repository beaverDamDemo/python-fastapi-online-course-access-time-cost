from sqlalchemy import Column, Integer, Float, ForeignKey
from models.base import Base


class Invoice(Base):
    __tablename__ = "fastapi_invoices"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(
        Integer,
        ForeignKey("fastapi_students.student_id", ondelete="CASCADE"),
        nullable=False,
    )
    koncni_znesek = Column(Float, nullable=False)
