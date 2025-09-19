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
    timestamp = Column(TIMESTAMP(timezone=True))
    used_credits = Column(Float)
    credit_price = Column(Float)
    student_id = Column(
        Integer, ForeignKey("fastapi_students.student_id", ondelete="CASCADE")
    )
