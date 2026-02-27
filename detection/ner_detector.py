"""
NER-based PII detection module.
Detects PII using Named Entity Recognition.
"""

import spacy
from utils.logger import get_logger

logger = get_logger("ner_detector")

class NERDetector:
    """NER-based PII detector."""
    
    def __init__(self, model_name="en_core_web_sm"):
        """Initialize NER model."""
        logger.info("Initializing NER model...")
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            # Fallback if model not downloaded
            import subprocess
            import sys
            logger.info(f"Model {model_name} not found. Downloading...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        self.pii_entities = {"PERSON", "ORG", "GPE", "LOC", "DATE"}

    def detect(self, text: str) -> list:
        """
        Detect PII in text using NER.
        
        Args:
            text: Input text to analyze
            
        Returns:
            List of detected entities with their details
        """
        doc = self.nlp(text)
        results = []
        for ent in doc.ents:
            if ent.label_ in self.pii_entities:
                results.append({
                    "text": ent.text,
                    "type": ent.label_,
                    "start": ent.start_char,
                    "end": ent.end_char,
                    "method": "ner"
                })
        
        logger.info(f"NER detection completed for text ({len(text)} chars)")
        return results

if __name__ == "__main__":
    detector = NERDetector()
    test_text = "Vyshnav lives in Hyderabad and works at Google."
    print(detector.detect(test_text))
