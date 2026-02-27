RISK_WEIGHTS = {
    "aadhaar": 50,
    "pan": 40,
    "credit_card": 70,
    "ssn": 70,
    "phone": 20,
    "email": 15,
    "person": 5,
    "location": 5
}

def calculate_risk(detected_pii):
    score = 0
    
    for item in detected_pii:
        # Support dict objects (dummy array) and Pydantic models
        if isinstance(item, dict):
            pii_type = item.get("type", "")
        else:
            pii_type = getattr(item, "type", "")
            
        score += RISK_WEIGHTS.get(str(pii_type).lower(), 0)
    
    if score >= 70:
        level = "CRITICAL"
    elif score >= 40:
        level = "HIGH"
    elif score >= 20:
        level = "MEDIUM"
    else:
        level = "LOW"

    return score, level
