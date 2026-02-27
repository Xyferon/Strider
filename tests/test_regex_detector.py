import pytest

from detection.regex_detector import RegexDetector


def test_regex_detector_email_and_phone():
    detector = RegexDetector()
    text = "Contact me at test@example.com or +1 123-456-7890."

    entities = detector.detect(text)

    # Ensure at least one email and one phone entity are detected
    types = {e["type"] for e in entities}
    assert "email" in types
    assert "phone" in types

    # All entities must follow the shared detection schema
    for e in entities:
        assert {"type", "masked_value", "confidence", "detection_method", "start_index", "end_index"} <= e.keys()
        assert isinstance(e["masked_value"], str)
        assert isinstance(e["confidence"], float)
        assert isinstance(e["start_index"], int)
        assert isinstance(e["end_index"], int)


def test_regex_detector_empty_input():
    detector = RegexDetector()
    assert detector.detect("") == []

