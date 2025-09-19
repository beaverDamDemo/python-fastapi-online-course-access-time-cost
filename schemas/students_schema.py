from pydantic import BaseModel, Field
from typing import Optional


class StudentCreate(BaseModel):
    firstname: str = Field(..., min_length=2, max_length=50)
    lastname: str = Field(..., min_length=2, max_length=50)
    address: str = Field(..., min_length=5, max_length=100)


class StudentUpdate(BaseModel):
    firstname: Optional[str] = Field(None, min_length=2)
    lastname: Optional[str] = Field(None, min_length=2)
    address: Optional[str] = Field(None, min_length=5)


class StudentOut(StudentCreate):
    student_id: int

    class Config:
        from_attributes = True
