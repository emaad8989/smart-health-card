# Smart Health Card

QR-based patient health record system (hackathon prototype).
**All data is synthetic. Never add real patient data.**

| Part | Tech | Owner |
|---|---|---|
| Backend and database | Python, FastAPI, SQLite | Emaad |
| Frontend | React, Vite | Ayush |

## How it works

1. Each sample patient has an ID such as `PAT001`.
2. The QR code contains that plain patient ID (nothing else).
3. The frontend scans the QR code and gets the ID.
4. The frontend calls `GET /patients/{patient_id}` to show the record.
5. A doctor adds a visit with `POST /patients/{patient_id}/consultations`.

## Run the backend (Windows PowerShell)

Needs Python 3.10+ and Git. Do this once:

```powershell
git clone https://github.com/emaad8989/smart-health-card.git
cd smart-health-card\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m app.seed
```

Every time you work:

```powershell
cd smart-health-card\backend
.\.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive docs (Swagger): http://127.0.0.1:8000/docs

If PowerShell blocks the activate script, run this once:
`Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned`

## Sample patients

| ID | Name | Blood group | Notes |
|---|---|---|---|
| PAT001 | Aarav Mehta | B+ | 1 consultation |
| PAT002 | Diya Kapoor | O+ | 2 consultations |
| PAT003 | Rohan Verma | A- | 1 consultation |
| PAT004 | Meera Nair | AB+ | no consultations (empty history) |
| PAT005 | Kabir Singh | O- | 1 consultation |

## API reference

### GET /health

Checks the server is running.

```json
{"status": "ok", "message": "Smart Health Card API is running"}
```

### GET /patients/{patient_id}

Example: `GET http://127.0.0.1:8000/patients/PAT002`

The ID is not case sensitive and surrounding spaces are ignored.
Consultations are sorted newest first.

Response `200`:

```json
{
  "patient_id": "PAT002",
  "full_name": "Diya Kapoor",
  "date_of_birth": "1985-11-03",
  "gender": "Female",
  "blood_group": "O+",
  "allergies": "None known",
  "medical_conditions": "Asthma",
  "consultations": [
    {
      "id": 3,
      "doctor_name": "Dr. Rao",
      "consultation_date": "2026-06-02T11:15:00",
      "symptoms": "Follow-up, no wheezing",
      "diagnosis": "Asthma well controlled",
      "prescription": "Continue inhaler",
      "notes": "Next review in 6 months"
    }
  ]
}
```

Unknown ID returns `404`:

```json
{"detail": "Patient PAT999 not found"}
```

### POST /patients/{patient_id}/consultations

Adds a consultation. The server sets the date and ID.

Request body (JSON):

```json
{
  "doctor_name": "Dr. Sharma",
  "symptoms": "Sore throat, mild fever",
  "diagnosis": "Viral throat infection",
  "prescription": "Rest, warm fluids",
  "notes": "Return if no improvement in 5 days"
}
```

- `doctor_name`, `symptoms` and `diagnosis` are required and cannot be empty.
- `prescription` and `notes` are optional (default is empty text).

Response `201`: the saved consultation, including its `id` and `consultation_date`.

Errors:

| Code | Meaning |
|---|---|
| 404 | Patient ID does not exist |
| 422 | Missing or empty required field (the response says which one) |

## Frontend notes

- The backend allows requests from `http://localhost:5173` and `http://127.0.0.1:5173`
  (Vite's default). If your app runs on another port, tell Emaad.
- Example call from React:

```js
const res = await fetch(`http://127.0.0.1:8000/patients/${patientId}`);
if (res.status === 404) {
  // show "Patient not found"
}
const patient = await res.json();
```

## Team workflow

- Emaad edits only `backend/`. Ayush edits only `frontend/`.
- Run `git pull` before you start work.
- Commit small and often, then `git push` at the end of each session.
- The database file is not in Git. Everyone creates theirs with `python -m app.seed`.