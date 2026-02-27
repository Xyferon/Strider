"""
NER-based PII detection module.
Detects PII using Named Entity Recognition.
"""

import spacy
from typing import List, Dict, Any

from utils.logger import get_logger

logger = get_logger("ner_detector")


def _mask(value: str) -> str:
    if not value:
        return ""
    if len(value) <= 2:
        return "*" * len(value)
    return value[0] + "*" * (len(value) - 2) + value[-1]


class NERDetector:
    """NER-based PII detector."""

    def __init__(self, model_name: str = "en_core_web_sm") -> None:
        """Initialize NER model."""
        logger.info("Initializing NER model...")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            import subprocess
            import sys

            logger.info(f"Model {model_name} not found. Downloading...")
            subprocess.check_call(
                [sys.executable, "-m", "spacy", "download", model_name]
            )
            self.nlp = spacy.load(model_name)

        self.pii_entities = {"PERSON", "ORG", "GPE", "LOC", "DATE"}

    def detect(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect PII in text using NER.

        Returns entities using the shared detection schema.
        """
        if not text:
            return []

        doc = self.nlp(text)
        results: List[Dict[str, Any]] = []
        for ent in doc.ents:
            if ent.label_ in self.pii_entities:
                value = ent.text
                results.append(
                    {
                        "type": ent.label_.lower(),
                        "raw_value": value,
                        "masked_value": _mask(value),
                        # Confidence is exposed via the public API and must
                        # be normalized between 0 and 1.
                        "confidence": 0.8,
                        # Align with public API contract: "regex" | "nlp".
                        "detection_method": "nlp",
                        "start_index": ent.start_char,
                        "end_index": ent.end_char,
                    }
                )

        logger.info(f"NER detection completed for text ({len(text)} chars)")
        return results

if __name__ == "__main__":
    detector = NERDetector()
    test_text = "Vyshnav lives in Hyderabad and works at Google."
    print(detector.detect(test_text))
