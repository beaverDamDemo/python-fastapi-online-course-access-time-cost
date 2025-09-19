from sqlalchemy import Column, Integer, String, Identity
from .base import Base
from sqlalchemy.orm import relationship


class Student(Base):
    __tablename__ = "fastapi_students"

    student_id = Column(Integer, Identity(always=True), primary_key=True, index=True)
    firstname = Column(String, nullable=True)
    lastname = Column(String, nullable=True)
    address = Column(String, nullable=True)

    invoices = relationship(
        "Invoice", backref="student", cascade="all, delete", passive_deletes=True
    )
