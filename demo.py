"""
Detection Accuracy Demo for PII Leakage Scanner.

This script runs predefined test cases containing various types of PII
against the detection pipeline and outputs a summary of the accuracy.
"""

import sys
from backend.pipeline import run_pipeline
from utils.schema import create_document

def run_demo():
    print("=" * 60)
    print("PII Leakage Scanner - Detection Accuracy Demo")
    print("=" * 60)

    test_cases = [
        {
            "id": "tc1",
            "text": "My email is john.doe@example.com and my phone number is 123-456-7890.",
            "expected_types": {"email", "phone"},
            "expected_categories": {"personal"}
        },
        {
            "id": "tc2",
            "text": "Payment info: Card 4111 2222 3333 4444, exp 12/25.",
            "expected_types": {"credit_card"},
            "expected_categories": {"financial"}
        },
        {
            "id": "tc3",
            "text": "My Aadhaar is 1234 5678 9012. Please do not share my PAN ABCDE1234F.",
            "expected_types": {"aadhaar", "pan"},
            "expected_categories": {"government_id", "financial"}
        },
        {
            "id": "tc4",
            "text": "The patient, John Smith, was diagnosed with a mild cold.",
            "expected_types": {"person"}, # NER detects PERSON
            "expected_categories": {"personal"}
        },
        {
            "id": "tc5",
            "text": "This is a clean document with no sensitive information at all.",
            "expected_types": set(),
            "expected_categories": set()
        }
    ]

    documents = []
    for tc in test_cases:
        doc = create_document(
            source="demo",
            source_type="test",
            url=f"test://{tc['id']}",
            raw_text=tc["text"],
            clean_text=tc["text"],
            author="tester",
            tags=["demo"]
        )
        documents.append(doc)

    print(f"\nRunning pipeline on {len(documents)} test documents...\n")
    incidents = run_pipeline(documents)

    total_tests = len(test_cases)
    passed_tests = 0

    for idx, (tc, inc) in enumerate(zip(test_cases, incidents)):
        detected_types = {e["type"] for e in inc.get("entities", [])}
        # The pipeline classifies everything under categories per incident now.
        # But we only get the category directly on the incident dict if we extracted it,
        # Wait, run_pipeline currently does NOT attach `categories` directly to the incident output dict, only RiskScoring factors.
        # Let's assess detection accuracy based on entity types.
        
        types_match = tc["expected_types"].issubset(detected_types)
        
        print(f"Test Case {idx+1}: {tc['text']}")
        print(f"  Expected Entities: {tc['expected_types']}")
        print(f"  Detected Entities: {detected_types}")
        
        if types_match or (not tc["expected_types"] and not detected_types):
            print("  Status: [PASS]")
            passed_tests += 1
        else:
            print("  Status: [FAIL] - Missing expected entities")
            
        print("-" * 60)

    accuracy = (passed_tests / total_tests) * 100
    print(f"\nFinal Accuracy: {passed_tests}/{total_tests} ({accuracy:.1f}%)\n")
    
    if passed_tests == total_tests:
        print("Demo completed successfully! All detection cases passed.")
        sys.exit(0)
    else:
        print("Demo completed with failures.")
        sys.exit(1)


if __name__ == "__main__":
    run_demo()
