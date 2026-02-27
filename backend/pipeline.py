"""
End-to-end pipeline orchestration:

Scraped documents -> detection -> classification -> risk scoring.
"""

from __future__ import annotations

from typing import List, Dict, Any

from detection.pii_combiner import PIICombiner
from backend.classifier import Classifier
from backend.risk_scoring import RiskScorer
from utils.logger import get_logger


logger = get_logger("pipeline")

_combiner = PIICombiner()
_classifier = Classifier()
_scorer = RiskScorer()


def run_pipeline(documents: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Run the full PII analysis pipeline over a list of documents.

    Returns a list of incident dicts with schema:
    - incident_id
    - risk_score
    - severity
    - entities (list of detection entities)
    plus selected document context fields.
    """
    incidents: List[Dict[str, Any]] = []

    for idx, doc in enumerate(documents):
        clean_text = doc.get("clean_text") or ""
        if not isinstance(clean_text, str):
            clean_text = str(clean_text)

        # Detection (regex + NER)
        entities = _combiner.combine(clean_text) if clean_text else []

        # Classification
        base_incident = _classifier.classify(
            {
                "incident_id": f"inc-{idx}",
                "entities": entities,
            }
        )

        # Risk scoring
        risk_info = _scorer.score({"entities": entities}, base_incident)

        # Context snippet is used by the public API but must never expose
        # raw unmasked sensitive values. Keep it high-level.
        context_snippet = ""
        if entities:
            context_snippet = f"{len(entities)} sensitive entities detected in document."

        incident = {
            "incident_id": base_incident["incident_id"],
            "risk_score": float(risk_info.get("score", 0.0)),
            "severity": str(risk_info.get("risk_level", "low")),
            "entities": base_incident["entities"],
            # Document context
            "source": doc.get("source"),
            "source_type": doc.get("source_type"),
            "url": doc.get("url"),
            "timestamp": doc.get("timestamp"),
            "author": doc.get("author"),
            "metadata": doc.get("metadata") or {},
            "context_snippet": context_snippet,
        }

        incidents.append(incident)

    logger.info(f"Pipeline completed for {len(documents)} documents")
    return incidents


__all__ = ["run_pipeline"]

