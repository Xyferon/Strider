from typing import List, Dict, Any

from backend.pipeline import run_pipeline
from backend.schemas import DetectionEntity, Incident
from utils.schema import create_document


def _make_doc(raw: str, clean: str, **meta: Any) -> Dict[str, Any]:
    return create_document(
        source="test",
        source_type="unit",
        url="https://example.com",
        raw_text=raw,
        clean_text=clean,
        author=meta.get("author"),
        tags=meta.get("tags"),
    )


def test_document_schema_has_required_fields():
    doc = _make_doc("raw", "clean", tags=["x"])
    for key in [
        "source",
        "source_type",
        "url",
        "timestamp",
        "author",
        "raw_text",
        "clean_text",
        "metadata",
    ]:
        assert key in doc

    assert isinstance(doc["metadata"], dict)
    assert isinstance(doc["metadata"].get("tags"), list)


def test_pipeline_handles_empty_and_single_document():
    # Empty dataset
    incidents: List[Dict[str, Any]] = run_pipeline([])
    assert incidents == []

    # Single simple document
    doc = _make_doc(
        "Contact john@example.com",
        "Contact john@example.com",
        tags=["email"],
    )
    incidents = run_pipeline([doc])
    assert len(incidents) == 1

    incident = incidents[0]
    # Validate incident schema via Pydantic model
    model = Incident(**incident)
    assert model.incident_id
    assert isinstance(model.entities, list)


def test_pipeline_handles_malformed_document():
    # Missing optional metadata and non-string clean_text
    bad_doc = {
        "source": "test",
        "source_type": "unit",
        "url": "https://example.com",
        "timestamp": "now",
        "author": None,
        "raw_text": None,
        "clean_text": 12345,  # non-string
        "metadata": None,
    }

    incidents = run_pipeline([bad_doc])
    assert len(incidents) == 1
    incident = Incident(**incidents[0])
    assert incident.metadata is not None

