from models.base import Base
from sqlalchemy import (
    Column,
    Integer,
    Float,
    TIMESTAMP,
    ForeignKey,
)


class InsertedData(Base):
    __tablename__ = "fastapi_inserted_data"

    id = Column(Integer, primary_key=True, index=True)
    casovna_znacka = Column(TIMESTAMP(timezone=True))
    poraba = Column(Float)
    dinamicne_cene = Column(Float)
    student_id = Column(
        Integer, ForeignKey("fastapi_students.student_id", ondelete="CASCADE")
    )
