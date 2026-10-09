from fastapi import FastAPI

app = FastAPI(
    title="Smart Health Card API",
    description="Backend for the QR-based patient health record system (prototype, synthetic data only).",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {"status": "ok", "message": "Smart Health Card API is running"}