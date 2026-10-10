from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import Base, engine, get_db

# Make sure the tables exist when the app starts.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Smart Health Card API",
    description="Backend for the QR-based patient health record system (prototype, synthetic data only).",
    version="0.2.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Health Card API is running"}


@app.get("/patients/{patient_id}", response_model=schemas.PatientOut)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = (
        db.query(models.Patient)
        .filter(models.Patient.patient_id == patient_id.strip().upper())
        .first()
    )
    if patient is None:
        raise HTTPException(status_code=404, detail=f"Patient {patient_id} not found")
    return patient