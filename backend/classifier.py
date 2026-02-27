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
        Groups specific entities into high-level categories.
        """
        incident_id = pii_data.get("incident_id")
        entities: List[Dict[str, Any]] = pii_data.get("entities", []) or []

        # Determine categories present
        detected_categories = set()
        for ent in entities:
            t = ent.get("type", "").lower()
            if t in ["credit_card", "pan", "bank_account", "routing_number"]:
                detected_categories.add("financial")
            elif t in ["aadhaar", "ssn", "passport"]:
                detected_categories.add("government_id")
            elif t in ["email", "phone", "person", "address"]:
                detected_categories.add("personal")
            elif t in ["health_record", "medical_condition"]:
                detected_categories.add("medical")
            else:
                detected_categories.add("other")

        classified = {
            "incident_id": incident_id,
            "risk_score": float(pii_data.get("risk_score", 0.0)),
            "severity": str(pii_data.get("severity", "low")),
            "entities": entities,
            "categories": list(detected_categories)
        }

        logger.info(f"Classification completed: {list(detected_categories)} for {len(entities)} entities")
        return classified
