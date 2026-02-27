"""
Regex-based PII detection module.
Detects PII using predefined regex patterns.
"""

import re
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger("regex_detector")


def _mask(value: str) -> str:
    """
    Simple masking helper: keep first and last character if possible,
    mask the middle.
    """
    if not value:
        return ""
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "*" * (len(value) - 2) + value[-1]


class RegexDetector:
    """Regex-based PII detector."""

    def __init__(self) -> None:
        """Initialize regex patterns for PII detection."""
        self.patterns = {
            "email": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "phone": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "aadhaar": r"\b\d{4}\s\d{4}\s\d{4}\b",
            "pan": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
            "credit_card": r"\b(?:\d[ -]*?){13,16}\b",
            "ip_address": r"\b(?:\d{1,3}\.){3}\d{1,3}\b",
        }

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text using regex patterns.

        Returns a list of entities following the shared detection schema:
        - type
        - masked_value
        - confidence
        - detection_method
        - start_index
        - end_index
        """
        if not text:
            return []

        results: List[Dict[str, Any]] = []
        for pii_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text):
                value = match.group()
                results.append(
                    {
                        "type": pii_type,
                        "masked_value": _mask(value),
                        "confidence": 0.9,
                        "detection_method": "regex",
                        "start_index": match.start(),
                        "end_index": match.end(),
                    }
                )

        logger.info(f"Regex detection completed for text ({len(text)} chars)")
        return results

if __name__ == "__main__":
    detector = RegexDetector()
    test_text = "Contact me at test@example.com or 9876543210. Aadhaar: 1234 5678 9012. PAN: ABCDE1234F"
    print(detector.detect(test_text))
