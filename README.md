# Smart Health Card: QR-Based Patient Health Record System

A working prototype for the Smart India Hackathon. A patient carries a printed card with QR codes. A doctor scans the card and instantly sees the patient's record. In an emergency, anyone can scan a separate emergency QR with a normal phone camera to see life-critical details, with no app and no login.

> All data in this prototype is **synthetic** (fictional patients PAT001 to PAT005). It is not connected to the official ABDM / ABHA network.

## Live demo

- Website: https://smart-health-card-bltg.onrender.com
- API documentation: https://smart-health-card-api.onrender.com/docs

The free hosting sleeps when idle, so the first load can take up to a minute.

## Key features

- **Doctor login:** username and password, signed tokens (JWT) that expire after 8 hours.
- **QR scanning:** the doctor QR contains only the patient ID, no medical data.
- **Patient record:** profile, blood group, allergies (highlighted in red), conditions and consultation history.
- **Add consultation:** doctor, symptoms, diagnosis, prescription and notes are saved permanently.
- **Emergency QR page (no login):** shows only blood group, allergies, major conditions and a tap-to-call emergency contact. The link carries a server-made signature (HMAC), so patient IDs cannot be guessed.
- **Access log:** every emergency scan, doctor view and override is recorded with the time.
- **Restricted records and emergency override:** a restricted record cannot be opened normally. A doctor must type a reason, which is permanently recorded in the access log.

## Technology

| Part | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, Pydantic |
| Database | SQLite (local), PostgreSQL on Neon (online) |
| Frontend | Plain HTML, CSS, JavaScript, html5-qrcode |
| Authentication | JWT (PyJWT), HMAC-signed emergency links |
| Hosting | Render (API and website) |
| QR and cards | Python `qrcode` library, 85.6 x 54 mm card layout at 300 DPI |

## Project structure

```
smart-health-card/
  backend/
    app/
      main.py            API endpoints
      models.py          database tables
      schemas.py         request and response shapes
      auth.py            doctor login and tokens
      emergency_link.py  signed emergency links
      access_log.py      access log helper
      migrate.py         adds new columns to older databases
      seed.py            synthetic sample patients
      generate_qr.py     QR code generator
      generate_cards.py  printable card generator
    requirements.txt
  frontend/
    login.html  dashboard.html  scan.html
    patient.html  emergency.html
    auth.js  config.js
```

## Run it locally

Requirements: Python 3.12 or newer, Git, VS Code with the Live Server extension.

Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The API runs at http://127.0.0.1:8000 (documentation at `/docs`). Locally, a development login is used. On the hosted version the login and secret key are set as environment variables and are never stored in the code.

Frontend: open the `frontend` folder in VS Code, right-click `login.html` and choose **Open with Live Server**.

## Configuration (hosted version)

Set these as environment variables on the server (never commit them):
`DATABASE_URL`, `ALLOWED_ORIGINS`, `DOCTOR_USERNAME`, `DOCTOR_PASSWORD`, `SECRET_KEY`.

## Limitations and future scope

- One shared doctor login, with no individual accounts or roles yet.
- No patient-side consent or OTP verification yet.
- No integration with the official ABDM / ABHA systems.
- Data is not encrypted at rest.
- Planned: individual doctor, nurse and admin accounts, patient consent, ABDM sandbox integration, queue and token system, document uploads, drug-allergy alerts.

## Team

Emaad (team leader: backend, database, API, integration, testing) and Ayush (frontend).