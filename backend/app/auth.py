import hmac
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

# Render sets the RENDER variable automatically, so we know we are live.
ON_RENDER = bool(os.getenv("RENDER"))

DOCTOR_USERNAME = os.getenv("DOCTOR_USERNAME")
DOCTOR_PASSWORD = os.getenv("DOCTOR_PASSWORD")
SECRET_KEY = os.getenv("SECRET_KEY")

# Live server: refuse to start without real settings (no default passwords online).
if ON_RENDER and not (DOCTOR_USERNAME and DOCTOR_PASSWORD and SECRET_KEY):
    raise RuntimeError("Set DOCTOR_USERNAME, DOCTOR_PASSWORD and SECRET_KEY in Render.")

# Laptop only: easy demo values so you can test without any setup.
DOCTOR_USERNAME = DOCTOR_USERNAME or "doctor"
DOCTOR_PASSWORD = DOCTOR_PASSWORD or "demo-password-123"
SECRET_KEY = SECRET_KEY or "local-dev-only-secret-key-0123456789abcdef"

TOKEN_HOURS = 8
bearer = HTTPBearer(auto_error=False)


def check_login(username: str, password: str) -> bool:
    """Compare in a way that doesn't leak how many characters matched."""
    user_ok = hmac.compare_digest(username.encode(), DOCTOR_USERNAME.encode())
    pass_ok = hmac.compare_digest(password.encode(), DOCTOR_PASSWORD.encode())
    return user_ok and pass_ok


def create_token(username: str) -> str:
    payload = {
        "sub": username,
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_HOURS),
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def require_doctor(credentials: HTTPAuthorizationCredentials | None = Depends(bearer)) -> str:
    """Put this on any endpoint that needs a logged-in doctor."""
    if credentials is None:
        raise HTTPException(status_code=401, detail="Login required")
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid or expired login")
    return payload["sub"]