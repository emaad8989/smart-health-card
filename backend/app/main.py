from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

# Make sure the tables exist when the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Health Card API",
    description="Backend for the QR-based patient health record system (prototype, synthetic data only).",
    version="0.4.0",
)

# Frontend addresses that are allowed to call this API (Vite's default port is 5173).
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


def find_patient(db: Session, patient_id: str) -> models.Patient:
    """Look up a patient by ID like PAT001, or raise a 404 error."""
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.patient_id == patient_id.strip().upper())
        .first()
    )
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Health Card API is running"}


@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    return find_patient(db, patient_id)


@app.post(
    "/patients/{patient_id}/consultations",
    response_model=schemas.ConsultationOut,
    status_code=201,
)
def add_consultation(
    patient_id: str,
    consultation: schemas.ConsultationCreate,
    db: Session = Depends(get_db),
):
    patient = find_patient(db, patient_id)

    new_consultation = models.Consultation(
        patient_pk=patient.id,
        **consultation.model_dump(),
    )
    db.add(new_consultation)
    db.commit()
    db.refresh(new_consultation)
    return new_consultation