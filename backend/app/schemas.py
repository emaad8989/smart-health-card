from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class ConsultationCreate(BaseModel):
    """What the doctor sends when adding a consultation."""

    doctor_name: str = Field(min_length=1, max_length=100)
    symptoms: str = Field(min_length=1)
    diagnosis: str = Field(min_length=1)
    prescription: str = ""
    notes: str = ""


class ConsultationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    doctor_name: str
    consultation_date: datetime
    symptoms: str
    diagnosis: str
    prescription: str
    notes: str


class PatientOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    patient_id: str
    full_name: str
    date_of_birth: date
    gender: str
    blood_group: str
    allergies: str
    medical_conditions: str
    restricted: bool = False
    consultations: list[ConsultationOut]


class LoginRequest(BaseModel):
    username: str
    password: str


class EmergencyOut(BaseModel):
    """Only life-critical details. Shown by the emergency QR, no login needed."""

    patient_id: str
    blood_group: str
    allergies: str
    medical_conditions: str
    emergency_contact_name: str
    emergency_contact_phone: str


class AccessLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    patient_id: str
    access_type: str
    accessed_by: str
    reason: str
    accessed_at: datetime


class OverrideRequest(BaseModel):
    """The doctor's reason for opening a restricted record in an emergency."""

    reason: str = Field(min_length=10, max_length=500)