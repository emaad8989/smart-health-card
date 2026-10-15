from datetime import date, datetime

from app import models
from app.database import Base, SessionLocal, engine

# All data below is fictional (synthetic) and for development only.
SAMPLE_PATIENTS = [
    {
        "patient_id": "PAT001",
        "full_name": "Aarav Mehta",
        "date_of_birth": date(1990, 4, 12),
        "gender": "Male",
        "blood_group": "B+",
        "allergies": "Penicillin",
        "medical_conditions": "Type 2 Diabetes",
        "emergency_contact_name": "Neha Mehta (Wife)",
        "emergency_contact_phone": "+91 00000 00001",
        "consultations": [
            {
                "doctor_name": "Dr. Sharma",
                "consultation_date": datetime(2026, 3, 5, 10, 30),
                "symptoms": "Increased thirst, fatigue",
                "diagnosis": "Elevated blood sugar",
                "prescription": "Metformin 500 mg twice daily",
                "notes": "Review in 3 months",
            },
        ],
    },
    {
        "patient_id": "PAT002",
        "full_name": "Diya Kapoor",
        "date_of_birth": date(1985, 11, 3),
        "gender": "Female",
        "blood_group": "O+",
        "allergies": "None known",
        "medical_conditions": "Asthma",
        "emergency_contact_name": "Arjun Kapoor (Husband)",
        "emergency_contact_phone": "+91 00000 00002",
        "consultations": [
            {
                "doctor_name": "Dr. Rao",
                "consultation_date": datetime(2026, 1, 18, 14, 0),
                "symptoms": "Wheezing at night",
                "diagnosis": "Mild asthma flare-up",
                "prescription": "Inhaler as needed",
                "notes": "Avoid dust exposure",
            },
            {
                "doctor_name": "Dr. Rao",
                "consultation_date": datetime(2026, 6, 2, 11, 15),
                "symptoms": "Follow-up, no wheezing",
                "diagnosis": "Asthma well controlled",
                "prescription": "Continue inhaler",
                "notes": "Next review in 6 months",
            },
        ],
    },
    {
        "patient_id": "PAT003",
        "full_name": "Rohan Verma",
        "date_of_birth": date(1972, 8, 25),
        "gender": "Male",
        "blood_group": "A-",
        "allergies": "Peanuts, Sulfa drugs",
        "medical_conditions": "Hypertension",
        "emergency_contact_name": "Sunita Verma (Wife)",
        "emergency_contact_phone": "+91 00000 00003",
        "restricted": True,
        "consultations": [
            {
                "doctor_name": "Dr. Iyer",
                "consultation_date": datetime(2026, 5, 9, 9, 45),
                "symptoms": "Headaches, dizziness",
                "diagnosis": "High blood pressure",
                "prescription": "Amlodipine 5 mg once daily",
                "notes": "Reduce salt intake",
            },
        ],
    },
    {
        "patient_id": "PAT004",
        "full_name": "Meera Nair",
        "date_of_birth": date(2001, 2, 14),
        "gender": "Female",
        "blood_group": "AB+",
        "allergies": "None known",
        "medical_conditions": "None",
        "emergency_contact_name": "Gopal Nair (Father)",
        "emergency_contact_phone": "+91 00000 00004",
        "consultations": [],
    },
    {
        "patient_id": "PAT005",
        "full_name": "Kabir Singh",
        "date_of_birth": date(1958, 7, 30),
        "gender": "Male",
        "blood_group": "O-",
        "allergies": "Latex",
        "medical_conditions": "Arthritis, High cholesterol",
        "emergency_contact_name": "Simran Singh (Daughter)",
        "emergency_contact_phone": "+91 00000 00005",
        "consultations": [
            {
                "doctor_name": "Dr. Sharma",
                "consultation_date": datetime(2026, 4, 21, 16, 0),
                "symptoms": "Joint pain in knees",
                "diagnosis": "Osteoarthritis flare-up",
                "prescription": "Paracetamol as needed",
                "notes": "Gentle exercise recommended",
            },
        ],
    },
]


def seed():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(models.Patient).count() > 0:
            print("Database already has patients. Nothing added.")
            return

        for data in SAMPLE_PATIENTS:
            consultation_rows = data["consultations"]
            patient_fields = {k: v for k, v in data.items() if k != "consultations"}

            patient = models.Patient(**patient_fields)
            for row in consultation_rows:
                patient.consultations.append(models.Consultation(**row))
            db.add(patient)

        db.commit()
        print(f"Added {len(SAMPLE_PATIENTS)} synthetic patients.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()