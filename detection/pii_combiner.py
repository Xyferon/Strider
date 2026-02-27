"""
PII detection combiner module.
Combines results from multiple detection methods.
"""

from detection.regex_detector import RegexDetector
from detection.ner_detector import NERDetector
from utils.logger import get_logger

logger = get_logger("pii_combiner")

class PIICombiner:
    """Combines PII detection results from multiple sources."""

    def __init__(self) -> None:
        """Initialize the combiner."""
        self.regex_detector = RegexDetector()
        self.ner_detector = NERDetector()
        logger.info("Initializing PII Combiner...")

    def combine(self, text: str) -> list:
        """
        Combine detection results from multiple methods and handle overlaps.

        Returns entities using the shared detection schema.
        """
        if not text:
            return []

        regex_results = self.regex_detector.detect(text)
        ner_results = self.ner_detector.detect(text)

        # Combine all results
        all_results = regex_results + ner_results

        # Simple deduplication based on span overlap
        # Priority: Regex (usually more specific for patterns) over NER
        sorted_results = sorted(
            all_results, key=lambda x: (x["start_index"], -x["end_index"])
        )

        merged_results = []
        if not sorted_results:
            return merged_results

        current = sorted_results[0]
        for next_res in sorted_results[1:]:
            # If start of next is within current end, they overlap
            if next_res["start_index"] < current["end_index"]:
                # Keep the first one encountered (acts as the "higher priority")
                continue
            merged_results.append(current)
            current = next_res

        merged_results.append(current)
        logger.info(
            f"PII results combined successfully: {len(merged_results)} entities found"
        )
        return merged_results

if __name__ == "__main__":
    combiner = PIICombiner()
    test_text = "John Doe (john.doe@email.com) lives in New York. Phone: +1 123-456-7890."
    print(combiner.combine(test_text))
