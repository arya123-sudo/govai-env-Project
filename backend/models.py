from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from database import Base


class Citizen(Base):
    __tablename__ = "citizens"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    income = Column(Float, nullable=False)
    fraud_risk = Column(Float, nullable=False)
    region = Column(String(100), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
