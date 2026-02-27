from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, conint, confloat


# ---------------------------------------------------------------------------
# Internal pipeline schemas (backwards compatible with existing tests)
# ---------------------------------------------------------------------------


class DetectionEntity(BaseModel):
    """
    Schema for detection output entities used in incidents.
    """

    type: str
    masked_value: str
    confidence: float
    detection_method: str
    start_index: int
    end_index: int


class Incident(BaseModel):
    """
    End-to-end incident schema used by the pipeline and internal consumers.
    """

    incident_id: str
    risk_score: float
    severity: str
    entities: List[DetectionEntity]

    # document context
    source: str | None = None
    source_type: str | None = None
    url: str | None = None
    timestamp: str | None = None
    author: str | None = None
    metadata: Dict[str, Any] = {}
    context_snippet: str | None = None


# ---------------------------------------------------------------------------
# Public API v1 schemas (stable contract for the frontend)
# ---------------------------------------------------------------------------


class Severity(str, Enum):
    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CRITICAL = "Critical"


class DetectionMethod(str, Enum):
    REGEX = "regex"
    NLP = "nlp"


class ErrorResponse(BaseModel):
    """
    Unified error payload:
    {"error": "description"}
    """

    error: str


class ScanTriggerResponseV1(BaseModel):
    """
    Response model for POST /scan.
    """

    message: Literal["Scan completed"] = "Scan completed"
    target: Optional[str] = None
    incidents_found: int
    scan_timestamp: datetime


class IncidentEntityV1(BaseModel):
    """
    Entity detail used in incident detail view.
    """

    type: str
    masked_value: str
    confidence: confloat(ge=0.0, le=1.0)
    detection_method: DetectionMethod


class IncidentDetailV1(BaseModel):
    """
    Detailed incident view for GET /incidents/{incident_id}.
    """

    incident_id: str
    source: str
    url: str
    timestamp: datetime
    severity: Severity
    risk_score: conint(ge=0, le=100)
    entities: List[IncidentEntityV1]
    context_snippet: str


class IncidentSummaryV1(BaseModel):
    """
    Summary row for incidents table (GET /incidents).
    """

    incident_id: str
    source: str
    timestamp: datetime
    severity: Severity
    risk_score: conint(ge=0, le=100)
    entity_count: int


class MetricsResponseV1(BaseModel):
    """
    Aggregated metrics for dashboard summary cards (GET /metrics).
    """

    total: int
    critical: int
    high: int
    medium: int
    low: int


class IdentityAggregateItemV1(BaseModel):
    """
    Identity-centric aggregation item for GET /identities.
    """

    email: str
    domain: str
    occurrences: int
    max_risk_score: conint(ge=0, le=100)
    highest_severity: Severity
    last_seen: datetime
    related_incident_ids: List[str]

