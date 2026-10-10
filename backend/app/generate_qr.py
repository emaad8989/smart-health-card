from pathlib import Path

import qrcode
from qrcode.constants import ERROR_CORRECT_H

from app.database import SessionLocal
from app.models import Patient

# Save the images in a "qr_codes" folder at the top of the project.
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "qr_codes"


def make_qr_image(text: str):
    """Build a print-friendly QR code: black on white, high error correction."""
    qr = qrcode.QRCode(
        error_correction=ERROR_CORRECT_H,  # survives scratches and smudges
        box_size=20,                       # large, sharp image for printing
        border=4,                          # blank margin scanners need
    )
    qr.add_data(text)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white")


def generate_qr_codes():
    OUTPUT_DIR.mkdir(exist_ok=True)

    db = SessionLocal()
    try:
        patients = db.query(Patient).order_by(Patient.patient_id).all()
        for patient in patients:
            # The QR holds ONLY the patient ID, never medical details.
            image = make_qr_image(patient.patient_id)
            file_path = OUTPUT_DIR / f"{patient.patient_id}.png"
            image.save(file_path)
            print(f"Created {file_path.name}  ->  encodes: {patient.patient_id}")
    finally:
        db.close()

    print(f"\nDone. {len(patients)} QR codes saved in: {OUTPUT_DIR}")


if __name__ == "__main__":
    generate_qr_codes()