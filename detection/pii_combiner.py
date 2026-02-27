"""
PII detection combiner module.
Combines results from multiple detection methods.
"""

try:
    from detection.regex_detector import RegexDetector
    from detection.ner_detector import NERDetector
except ModuleNotFoundError:
    from regex_detector import RegexDetector
    from ner_detector import NERDetector

from utils.logger import get_logger

logger = get_logger("pii_combiner")

class PIICombiner:
    """Combines PII detection results from multiple sources."""
    
    def __init__(self):
        """Initialize the combiner."""
        self.regex_detector = RegexDetector()
        self.ner_detector = NERDetector()
        logger.info("Initializing PII Combiner...")
    
    def combine(self, text: str) -> list:
        """
        Combine detection results from multiple methods and handle overlaps.
        
        Args:
            text: Input text to analyze
            
        Returns:
            Combined and deduplicated detection results
        """
        regex_results = self.regex_detector.detect(text)
        ner_results = self.ner_detector.detect(text)
        
        # Combine all results
        all_results = regex_results + ner_results
        
        # Simple deduplication based on span overlap
        # Priority: Regex (usually more specific for patterns) over NER
        sorted_results = sorted(all_results, key=lambda x: (x['start'], -x['end']))
        
        merged_results = []
        if not sorted_results:
            return merged_results
            
        current = sorted_results[0]
        for next_res in sorted_results[1:]:
            # If start of next is within current end, they overlap
            if next_res['start'] < current['end']:
                # Keep the more specific one or the one with higher priority
                # Here we just keep the first one found in sorted list
                continue
            else:
                merged_results.append(current)
                current = next_res
        
        merged_results.append(current)
        logger.info(f"PII results combined successfully: {len(merged_results)} entities found")
        return merged_results

if __name__ == "__main__":
    combiner = PIICombiner()
    test_text = "John Doe (john.doe@email.com) lives in New York. Phone: +1 123-456-7890."
    print(combiner.combine(test_text))
