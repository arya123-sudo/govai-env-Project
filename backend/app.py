from fastapi import FastAPI, Depends, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import Optional

from database import engine, Base, SessionLocal
from models import Citizen
from schemas import (
    CitizenCreate,
    CitizenUpdate,
    CitizenResponse,
    StatsResponse,
    PaginatedCitizens,
)

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="GovAI API",
    description="Government AI Citizen Management System",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Database Dependency ────────────────────────────────────────────────────────

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ── Health Check ───────────────────────────────────────────────────────────────

@app.get("/", tags=["Health"])
def home():
    return {"message": "GovAI Backend Running", "version": "2.0.0"}


# ── Citizens ───────────────────────────────────────────────────────────────────

@app.post(
    "/citizens",
    response_model=CitizenResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["Citizens"],
    summary="Register a new citizen",
)
def create_citizen(citizen: CitizenCreate, db: Session = Depends(get_db)):
    new_citizen = Citizen(**citizen.model_dump())
    db.add(new_citizen)
    db.commit()
    db.refresh(new_citizen)
    return new_citizen


@app.get(
    "/citizens",
    response_model=PaginatedCitizens,
    tags=["Citizens"],
    summary="List all citizens with optional filters and pagination",
)
def get_citizens(
    region: Optional[str] = Query(None, description="Filter by region"),
    min_income: Optional[float] = Query(None, ge=0, description="Minimum income"),
    max_income: Optional[float] = Query(None, ge=0, description="Maximum income"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db),
):
    query = db.query(Citizen)

    if region:
        query = query.filter(Citizen.region.ilike(f"%{region}%"))
    if min_income is not None:
        query = query.filter(Citizen.income >= min_income)
    if max_income is not None:
        query = query.filter(Citizen.income <= max_income)

    total = query.count()
    citizens = query.offset((page - 1) * page_size).limit(page_size).all()

    return PaginatedCitizens(
        total=total,
        page=page,
        page_size=page_size,
        citizens=citizens,
    )


@app.get(
    "/citizens/{citizen_id}",
    response_model=CitizenResponse,
    tags=["Citizens"],
    summary="Get a single citizen by ID",
)
def get_citizen(citizen_id: int, db: Session = Depends(get_db)):
    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with id {citizen_id} not found",
        )
    return citizen


@app.patch(
    "/citizens/{citizen_id}",
    response_model=CitizenResponse,
    tags=["Citizens"],
    summary="Partially update a citizen's record",
)
def update_citizen(
    citizen_id: int,
    updates: CitizenUpdate,
    db: Session = Depends(get_db),
):
    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with id {citizen_id} not found",
        )

    for field, value in updates.model_dump(exclude_none=True).items():
        setattr(citizen, field, value)

    db.commit()
    db.refresh(citizen)
    return citizen


@app.delete(
    "/citizens/{citizen_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["Citizens"],
    summary="Remove a citizen record",
)
def delete_citizen(citizen_id: int, db: Session = Depends(get_db)):
    citizen = db.query(Citizen).filter(Citizen.id == citizen_id).first()
    if not citizen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Citizen with id {citizen_id} not found",
        )
    db.delete(citizen)
    db.commit()


# ── Analytics ──────────────────────────────────────────────────────────────────

@app.get(
    "/stats",
    response_model=StatsResponse,
    tags=["Analytics"],
    summary="Dashboard summary statistics",
)
def get_stats(db: Session = Depends(get_db)):
    total = db.query(Citizen).count()

    high_risk = (
        db.query(Citizen).filter(Citizen.fraud_risk > 0.7).count()
    )

    eligible = (
        db.query(Citizen)
        .filter(Citizen.income < 20000, Citizen.fraud_risk < 0.5)
        .count()
    )

    return StatsResponse(
        total_citizens=total,
        high_risk_cases=high_risk,
        eligible_citizens=eligible,
        high_risk_percentage=round((high_risk / total * 100) if total else 0, 2),
        eligibility_percentage=round((eligible / total * 100) if total else 0, 2),
    )


@app.get(
    "/high-risk-citizens",
    response_model=list[CitizenResponse],
    tags=["Analytics"],
    summary="Citizens with fraud risk above 0.7",
)
def get_high_risk_citizens(
    threshold: float = Query(0.7, ge=0.0, le=1.0, description="Fraud risk threshold"),
    db: Session = Depends(get_db),
):
    return (
        db.query(Citizen)
        .filter(Citizen.fraud_risk > threshold)
        .order_by(Citizen.fraud_risk.desc())
        .all()
    )
