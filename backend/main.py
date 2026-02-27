from fastapi import FastAPI
from models.schemas import ScanRequest, ScanResponse, PIIDetected
from classifier.risk_engine import calculate_risk

app = FastAPI(title="PII Leakage Scanner API", description="API for scanning and classifying PII leaks")

@app.post("/scan", response_model=ScanResponse)
def scan_data(request: ScanRequest):
    
    # TEMP: Replace this with actual detection module call
    dummy_detected = [
        {"type": "email", "value": "test@gmail.com"},
        {"type": "aadhaar", "value": "1234 5678 9012"}
    ]
    
    score, level = calculate_risk(dummy_detected)

    return ScanResponse(
        source=request.source,
        detected_pii=[PIIDetected(**item) for item in dummy_detected],
        risk_score=score,
        risk_level=level
    )

@app.get("/health")
def health_check():
    return {"status": "ok"}
