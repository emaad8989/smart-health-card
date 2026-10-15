from sqlalchemy import inspect, text

from app.database import engine
from app.seed import SAMPLE_PATIENTS

NEW_PATIENT_COLUMNS = {
    "emergency_contact_name": "VARCHAR(100) DEFAULT ''",
    "emergency_contact_phone": "VARCHAR(20) DEFAULT ''",
    "restricted": "BOOLEAN DEFAULT FALSE",
}


def add_missing_columns():
    """Add new columns to an existing patients table and fill in sample data (safe to run every start)."""
    existing = {col["name"] for col in inspect(engine).get_columns("patients")}

    with engine.begin() as conn:
        for name, definition in NEW_PATIENT_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE patients ADD COLUMN {name} {definition}"))

        # Fill in contacts for sample patients that don't have one yet.
        for p in SAMPLE_PATIENTS:
            conn.execute(
                text(
                    "UPDATE patients SET emergency_contact_name = :n, emergency_contact_phone = :ph "
                    "WHERE patient_id = :pid AND "
                    "(emergency_contact_name IS NULL OR emergency_contact_name = '')"
                ),
                {
                    "n": p["emergency_contact_name"],
                    "ph": p["emergency_contact_phone"],
                    "pid": p["patient_id"],
                },
            )

        # Make sure the sample patients that should be restricted are marked as restricted.
        for p in SAMPLE_PATIENTS:
            if p.get("restricted"):
                conn.execute(
                    text(
                        "UPDATE patients SET restricted = :r "
                        "WHERE patient_id = :pid AND (restricted IS NULL OR restricted = :f)"
                    ),
                    {"r": True, "f": False, "pid": p["patient_id"]},
                )