import os

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app import access_log, auth, emergency_link, models, schemas
from app.database import Base, engine, get_db
from app.migrate import add_missing_columns
from app.seed import seed

# Make sure the tables exist when the app starts.
Base.metadata.create_all(bind=engine)

# Add any new columns to an older database (safe to run every time).
add_missing_columns()

# Load the synthetic sample patients if the database is empty (skipped if it already has data).
if os.getenv("AUTO_SEED", "true").lower() == "true":
    seed()

app = FastAPI(
    title="Smart Health Card API",
    description="Backend for the QR-based patient health record system (prototype, synthetic data only).",
    version="0.9.0",
)

# Frontend addresses allowed to call this API.
DEFAULT_ORIGINS = (
    "http://localhost:5173,http://127.0.0.1:5173,"
    "http://localhost:5500,http://127.0.0.1:5500"
)
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv("ALLOWED_ORIGINS", DEFAULT_ORIGINS).split(",")
    if origin.strip()
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


@app.post("/login")
def login(credentials: schemas.LoginRequest):
    if not auth.check_login(credentials.username, credentials.password):
        raise HTTPException(status_code=401, detail="Wrong username or password")
    return {"access_token": auth.create_token(credentials.username), "token_type": "bearer"}


@app.get("/emergency/{patient_id}", response_model=schemas.EmergencyOut)
def get_emergency_info(patient_id: str, sig: str = "", db: Session = Depends(get_db)):
    """PUBLIC (no login), but only with the correct signature from the card's emergency QR.
    Returns only life-critical details, nothing else."""
    if not emergency_link.signature_is_valid(patient_id, sig):
        raise HTTPException(status_code=403, detail="Invalid emergency link")

    patient = find_patient(db, patient_id)
    result = schemas.EmergencyOut(
        patient_id=patient.patient_id,
        blood_group=patient.blood_group or "",
        allergies=patient.allergies or "",
        medical_conditions=patient.medical_conditions or "",
        emergency_contact_name=patient.emergency_contact_name or "",
        emergency_contact_phone=patient.emergency_contact_phone or "",
    )
    access_log.record_access(db, result.patient_id, "emergency", "emergency QR scan (no login)")
    return result


@app.get(
    "/patients/{patient_id}",
    response_model=schemas.PatientOut,
    dependencies=[Depends(auth.require_doctor)],
)
def get_patient(patient_id: str, db: Session = Depends(get_db)):
    patient = find_patient(db, patient_id)

    # Restricted records need the emergency override (with a typed reason) to open.
    if patient.restricted:
        raise HTTPException(status_code=403, detail="RESTRICTED")

    access_log.record_access(db, patient.patient_id, "doctor", "doctor login")
    return patient


@app.post(
    "/patients/{patient_id}/override",
    response_model=schemas.PatientOut,
    dependencies=[Depends(auth.require_doctor)],
)
def break_glass(patient_id: str, request: schemas.OverrideRequest, db: Session = Depends(get_db)):
    """Emergency override: opens the full record, but only with a typed reason, which is logged."""
    patient = find_patient(db, patient_id)
    access_log.record_access(
        db,
        patient.patient_id,
        "break_glass",
        "doctor login (emergency override)",
        request.reason.strip(),
    )
    return patient


@app.get(
    "/patients/{patient_id}/access-log",
    response_model=list[schemas.AccessLogOut],
    dependencies=[Depends(auth.require_doctor)],
)
def get_access_log(patient_id: str, db: Session = Depends(get_db)):
    """Who opened this patient's record and when (newest first)."""
    patient = find_patient(db, patient_id)
    return (
        db.query(models.AccessLog)
        .filter(models.AccessLog.patient_id == patient.patient_id)
        .order_by(models.AccessLog.accessed_at.desc(), models.AccessLog.id.desc())
        .all()
    )


@app.post(
    "/patients/{patient_id}/consultations",
    response_model=schemas.ConsultationOut,
    status_code=201,
    dependencies=[Depends(auth.require_doctor)],
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