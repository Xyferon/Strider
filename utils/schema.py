"""
Shared document/schema helpers to keep data structures consistent
across scrapers, detection, classification, and the backend.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


@dataclass
class Document:
    source: str
    source_type: str
    url: str
    timestamp: str
    author: Optional[str]
    raw_text: str
    clean_text: str
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data.setdefault("metadata", {})
        tags = data["metadata"].get("tags")
        if tags is None:
            data["metadata"]["tags"] = []
        return data


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def create_document(
    *,
    source: str,
    source_type: str,
    url: str,
    raw_text: str,
    clean_text: str,
    author: Optional[str] = None,
    tags: Optional[List[str]] = None,
    **extra_metadata: Any,
) -> Dict[str, Any]:
    """
    Factory used by scrapers to emit schema-compliant documents.
    """
    metadata: Dict[str, Any] = dict(extra_metadata)
    metadata["tags"] = list(tags or [])

    doc = Document(
        source=source,
        source_type=source_type,
        url=url,
        timestamp=_now_iso(),
        author=author,
        raw_text=raw_text or "",
        clean_text=clean_text or "",
        metadata=metadata,
    )
    return doc.to_dict()


__all__ = ["Document", "create_document"]

