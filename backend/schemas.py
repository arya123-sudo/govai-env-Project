from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class CitizenCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    income: float = Field(..., ge=0, description="Annual income in INR")
    fraud_risk: float = Field(..., ge=0.0, le=1.0, description="Fraud risk score between 0 and 1")
    region: str = Field(..., min_length=1, max_length=100)

    @field_validator("name")
    @classmethod
    def name_must_not_be_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name must not be blank")
        return v.strip()


class CitizenUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    income: Optional[float] = Field(None, ge=0)
    fraud_risk: Optional[float] = Field(None, ge=0.0, le=1.0)
    region: Optional[str] = Field(None, min_length=1, max_length=100)


class CitizenResponse(BaseModel):
    id: int
    name: str
    income: float
    fraud_risk: float
    region: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class StatsResponse(BaseModel):
    total_citizens: int
    high_risk_cases: int
    eligible_citizens: int
    high_risk_percentage: float
    eligibility_percentage: float


class PaginatedCitizens(BaseModel):
    total: int
    page: int
    page_size: int
    citizens: list[CitizenResponse]
