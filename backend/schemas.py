from pydantic import BaseModel
from typing import List

class PIIDetected(BaseModel):
    type: str
    value: str

class ScanRequest(BaseModel):
    source: str
    content: str

class ScanResponse(BaseModel):
    source: str
    detected_pii: List[PIIDetected]
    risk_score: int
    risk_level: str
