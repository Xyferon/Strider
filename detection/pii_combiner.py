"""
PII detection combiner module.
Combines results from multiple detection methods.
"""

from utils.logger import get_logger

logger = get_logger("pii_combiner")


class PIICombiner:
    """Combines PII detection results from multiple sources."""
    
    def __init__(self):
        """Initialize the combiner."""
        logger.info("Initializing PII Combiner...")
    
    def combine(self, regex_results: dict, ner_results: dict) -> dict:
        """
        Combine detection results from multiple methods.
        
        Args:
            regex_results: Results from regex detector
            ner_results: Results from NER detector
            
        Returns:
            Combined detection results
        """
        combined = {
            'regex': regex_results,
            'ner': ner_results,
            'confidence_score': 0.0
        }
        
        logger.info("PII results combined successfully")
        return combined
