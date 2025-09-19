import os
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    Float,
    TIMESTAMP,
    Identity,
)
from sqlalchemy.orm import sessionmaker, declarative_base
import models
from models.base import Base
from models import invoices_model, students_model

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
print("Connecting to DATABASE_URL:", DATABASE_URL)
print("Connecting to os.getenv(:", os.getenv("DATABASE_URL"))

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
Base.metadata.create_all(bind=engine)
