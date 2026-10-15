from sqlalchemy.orm import Session

from app import models


def record_access(db: Session, patient_id: str, access_type: str, accessed_by: str, reason: str = ""):
    """Save one line in the access log."""
    db.add(
        models.AccessLog(
            patient_id=patient_id,
            access_type=access_type,
            accessed_by=accessed_by,
            reason=reason,
        )
    )
    db.commit()