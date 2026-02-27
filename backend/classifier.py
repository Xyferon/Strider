"""
Classification module for categorizing detected PII.
"""

from typing import Dict, Any, List

from utils.logger import get_logger

logger = get_logger("classifier")


class Classifier:
    """Classifies detected PII into high-level incidents."""

    def __init__(self) -> None:
        """Initialize classifier."""
        logger.info("Initializing Classifier...")
        self.categories = ["personal", "financial", "medical", "government_id"]

    def classify(self, pii_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Classify detected PII and produce an incident-level structure.

        The returned dict follows the classification schema:
        - incident_id
        - risk_score  (may be updated by risk scoring)
        - severity    (may be updated by risk scoring)
        - entities
        """
        incident_id = pii_data.get("incident_id")
        entities: List[Dict[str, Any]] = pii_data.get("entities", []) or []

        classified = {
            "incident_id": incident_id,
            "risk_score": float(pii_data.get("risk_score", 0.0)),
            "severity": str(pii_data.get("severity", "low")),
            "entities": entities,
        }

        logger.info("Classification completed")
        return classified
