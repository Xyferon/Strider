"""
Risk scoring module for assessing PII exposure risk.
"""

from utils.logger import get_logger

logger = get_logger("risk_scoring")


class RiskScorer:
    """Scores risk level based on detected PII."""
    
    def __init__(self):
        """Initialize risk scorer."""
        logger.info("Initializing Risk Scorer...")
    
    def score(self, pii_data: dict, classification: dict) -> dict:
        """
        Score risk based on PII type and volume.
        """
        entities = pii_data.get("entities", [])
        categories = classification.get("categories", [])
        
        score: float = 0.0
        factors = []
        
        # Base score on categories
        if "financial" in categories:
            score += 0.5
            factors.append("Financial data exposed")
        if "government_id" in categories:
            score += 0.6
            factors.append("Government ID exposed")
        if "medical" in categories:
            score += 0.6
            factors.append("Medical records exposed")
        if "personal" in categories:
            score += 0.2
            factors.append("Personal data exposed")
            
        # Add score based on volume of entities
        volume = len(entities)
        if volume > 10:
            score += 0.4
            factors.append("High volume of PII")
        elif volume > 3:
            score += 0.2
            factors.append("Medium volume of PII")
            
        # Cap score at 1.0
        score = min(score, 1.0)
        
        # Determine risk level
        if score >= 0.8:
            risk_level = "critical"
        elif score >= 0.6:
            risk_level = "high"
        elif score >= 0.3:
            risk_level = "medium"
        else:
            risk_level = "low"
            if len(entities) == 0:
                risk_level = "none"

        risk_score = {
            'risk_level': risk_level,
            'score': round(score, 2),
            'factors': factors
        }
        
        logger.info(f"Risk scoring completed: {risk_level} ({score})")
        return risk_score
