from datetime import date, datetime

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(20), unique=True, index=True)  # e.g. "PAT001"
    full_name: Mapped[str] = mapped_column(String(100))
    date_of_birth: Mapped[date] = mapped_column(Date)
    gender: Mapped[str] = mapped_column(String(20))
    blood_group: Mapped[str] = mapped_column(String(5))
    allergies: Mapped[str] = mapped_column(Text, default="")
    medical_conditions: Mapped[str] = mapped_column(Text, default="")
    emergency_contact_name: Mapped[str] = mapped_column(String(100), default="")
    emergency_contact_phone: Mapped[str] = mapped_column(String(20), default="")
    restricted: Mapped[bool] = mapped_column(Boolean, default=False)  # needs emergency override to open

    consultations: Mapped[list["Consultation"]] = relationship(
        back_populates="patient",
        order_by="Consultation.consultation_date.desc()",
    )


class Consultation(Base):
    __tablename__ = "consultations"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_pk: Mapped[int] = mapped_column(ForeignKey("patients.id"))
    doctor_name: Mapped[str] = mapped_column(String(100))
    consultation_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)
    symptoms: Mapped[str] = mapped_column(Text)
    diagnosis: Mapped[str] = mapped_column(Text)
    prescription: Mapped[str] = mapped_column(Text, default="")
    notes: Mapped[str] = mapped_column(Text, default="")

    patient: Mapped["Patient"] = relationship(back_populates="consultations")


class AccessLog(Base):
    """One row every time a patient's record is opened."""

    __tablename__ = "access_logs"

    id: Mapped[int] = mapped_column(primary_key=True)
    patient_id: Mapped[str] = mapped_column(String(20), index=True)  # e.g. "PAT001"
    access_type: Mapped[str] = mapped_column(String(20))  # "emergency", "doctor", "break_glass"
    accessed_by: Mapped[str] = mapped_column(String(100), default="")
    reason: Mapped[str] = mapped_column(Text, default="")
    accessed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.now)