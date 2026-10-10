from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


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
    consultations: list[ConsultationOut]