from backend.risk_engine import calculate_risk


def test_calculate_risk_levels():
    # Low risk: no known PII types
    score, level = calculate_risk([])
    assert score == 0
    assert level == "LOW"

    # Medium risk: one phone (20)
    score, level = calculate_risk([{"type": "phone"}])
    assert score == 20
    assert level == "MEDIUM"

    # High risk: PAN (40)
    score, level = calculate_risk([{"type": "pan"}])
    assert score == 40
    assert level == "HIGH"

    # Critical risk: credit card (70)
    score, level = calculate_risk([{"type": "credit_card"}])
    assert score == 70
    assert level == "CRITICAL"

