from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, String, Text
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