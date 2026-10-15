import hashlib
import hmac

from app.auth import SECRET_KEY


def _key() -> bytes:
    return SECRET_KEY if isinstance(SECRET_KEY, bytes) else str(SECRET_KEY).encode()


def make_signature(patient_id: str) -> str:
    """A short code only this server can create for a given patient ID."""
    message = ("emergency:" + patient_id.strip().upper()).encode()
    return hmac.new(_key(), message, hashlib.sha256).hexdigest()[:12]


def signature_is_valid(patient_id: str, signature: str) -> bool:
    expected = make_signature(patient_id).encode()
    return hmac.compare_digest(expected, (signature or "").encode())