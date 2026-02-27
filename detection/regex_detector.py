"""
Regex-based PII detection module.
Detects PII using predefined regex patterns.
"""

import re
from utils.logger import get_logger

logger = get_logger("regex_detector")

class RegexDetector:
    """Regex-based PII detector."""
    
    def __init__(self):
        """Initialize regex patterns for PII detection."""
        self.patterns = {
            "EMAIL": r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}",
            "PHONE": r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}",
            "AADHAAR": r"\b\d{4}\s\d{4}\s\d{4}\b",
            "PAN": r"\b[A-Z]{5}[0-9]{4}[A-Z]{1}\b",
            "CREDIT_CARD": r"\b(?:\d[ -]*?){13,16}\b",
            "IP_ADDRESS": r"\b(?:\d{1,3}\.){3}\d{1,3}\b"
        }
    
    def detect(self, text: str) -> list:
        """
        Detect PII in text using regex patterns.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected PII matches with their details
        """
        results = []
        for pii_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                results.append({
                    "text": match.group(),
                    "type": pii_type,
                    "start": match.start(),
                    "end": match.end(),
                    "method": "regex"
                })
        
        logger.info(f"Regex detection completed for text ({len(text)} chars)")
        return results

if __name__ == "__main__":
    detector = RegexDetector()
    test_text = "Contact me at test@example.com or 9876543210. Aadhaar: 1234 5678 9012. PAN: ABCDE1234F"
    print(detector.detect(test_text))
