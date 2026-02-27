from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, Iterable, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.requests import Request

from backend.pipeline import run_pipeline
from backend.schemas import (
    ErrorResponse,
    IdentityAggregateItemV1,
    IncidentDetailV1,
    IncidentEntityV1,
    IncidentSummaryV1,
    MetricsResponseV1,
    ScanTriggerResponseV1,
    Severity,
    DetectionMethod,
)
from scraper.github_scraper import scrape_github
from scraper.pastebin_scraper import scrape_pastebin
from utils.dedup import Deduplicator
from utils.logger import get_logger


logger = get_logger("api")

app = FastAPI(
    title="PII Leakage Scanner API",
    description="Stable API for scanning and classifying PII leaks",
)

# CORS configuration for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# In-memory store for the latest scan results
_INCIDENT_STORE: Dict[str, Dict[str, Any]] = {}
_LAST_SCAN_TIMESTAMP: datetime | None = None


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _normalize_severity(value: Any) -> Severity:
    """
    Map internal severity strings to the public enum.
    """
    if isinstance(value, Severity):
        return value

    text = str(value or "").strip().lower()
    if text == "critical":
        return Severity.CRITICAL
    if text == "high":
        return Severity.HIGH
    if text == "medium":
        return Severity.MEDIUM
    return Severity.LOW


def _to_detection_method(value: Any) -> DetectionMethod:
    text = str(value or "").strip().lower()
    if text == "regex":
        return DetectionMethod.REGEX
    # Treat any non-regex detector as NLP to match the contract.
    return DetectionMethod.NLP


def _parse_timestamp(raw: Any) -> datetime:
    if isinstance(raw, datetime):
        return raw
    if not raw:
        return _now_utc()
    try:
        # datetime.fromisoformat handles ISO8601 strings.
        return datetime.fromisoformat(str(raw))
    except Exception:
        return _now_utc()


def _run_full_scan(target: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Run scraper -> deduplication -> detection/classification/risk pipeline.

    Results are stored in memory for subsequent /metrics and /incidents calls.
    If target is provided, only documents matching the target are processed.
    """
    global _INCIDENT_STORE, _LAST_SCAN_TIMESTAMP

    all_documents: List[Dict[str, Any]] = []

    # Scrapers (synchronous, executed inside FastAPI's threadpool)
    try:
        github_docs = scrape_github()
        all_documents.extend(github_docs)
        logger.info("GitHub scraper collected %d documents", len(github_docs))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("GitHub scraper failed: %s", exc)

    try:
        pastebin_docs = scrape_pastebin()
        all_documents.extend(pastebin_docs)
        logger.info("Pastebin scraper collected %d documents", len(pastebin_docs))
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.error("Pastebin scraper failed: %s", exc)

    # Deduplication
    dedup = Deduplicator()
    unique_documents: List[Dict[str, Any]] = []
    for doc in all_documents:
        clean_text = str(doc.get("clean_text") or "")
        if dedup.is_duplicate(clean_text):
            continue
        unique_documents.append(doc)

    incidents = run_pipeline(unique_documents, target=target)

    # Store results in memory for subsequent reads
    _INCIDENT_STORE = {inc["incident_id"]: inc for inc in incidents}
    _LAST_SCAN_TIMESTAMP = _now_utc()

    logger.info(
        "Full scan completed: %d documents -> %d incidents",
        len(unique_documents),
        len(incidents),
    )
    return incidents


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    message = exc.detail if isinstance(exc.detail, str) else str(exc.detail)
    return JSONResponse(status_code=exc.status_code, content={"error": message})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    logger.warning("Request validation error: %s", exc)
    return JSONResponse(status_code=422, content={"error": "Invalid request"})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error("Unhandled exception: %s", exc)
    return JSONResponse(status_code=500, content={"error": "Internal server error"})


@app.get("/health", response_model=dict)
def health_check() -> Dict[str, str]:
    """
    Simple liveness check used by the frontend.
    """
    return {"status": "running"}


@app.post("/scan", response_model=ScanTriggerResponseV1)
def trigger_scan(target: str | None = Query(default=None)) -> ScanTriggerResponseV1:
    """
    Trigger the full pipeline:
    - Run scrapers
    - Run detection
    - Run classification
    - Run risk scoring
    - Store results in memory
    """
    try:
        incidents = _run_full_scan(target=target)
    except Exception as exc:  # pragma: no cover - defensive
        logger.error("Scan failed: %s", exc)
        raise HTTPException(status_code=500, detail="Scan failed")

    ts = _LAST_SCAN_TIMESTAMP or _now_utc()
    return ScanTriggerResponseV1(
        target=target,
        incidents_found=len(incidents),
        scan_timestamp=ts,
    )


def _severity_for_max_score(
    candidates: List[tuple[float, Severity]],
) -> Severity:
    """
    Given (score, severity) pairs, return the severity for the highest score.
    """
    if not candidates:
        return Severity.LOW
    best_score, best_sev = sorted(candidates, key=lambda x: x[0], reverse=True)[0]
    return best_sev


def aggregate_identities(
    incidents: Iterable[Dict[str, Any]],
) -> List[IdentityAggregateItemV1]:
    """
    Group incidents by EMAIL entities (identity-centric view).
    """
    buckets: Dict[str, Dict[str, Any]] = {}

    for inc in incidents:
        incident_id = str(inc.get("incident_id") or "")
        risk_score = float(inc.get("risk_score") or 0.0)
        severity = _normalize_severity(inc.get("severity"))
        ts = _parse_timestamp(inc.get("timestamp") or _LAST_SCAN_TIMESTAMP)

        for ent in inc.get("entities") or []:
            ent_type = str(ent.get("type") or "")
            if ent_type.upper() != "EMAIL":
                continue

            email = str(ent.get("masked_value") or "").strip()
            if not email:
                continue

            if "@" in email:
                domain = email.split("@", 1)[1]
            else:
                domain = ""

            entry = buckets.setdefault(
                email,
                {
                    "email": email,
                    "domain": domain,
                    "occurrences": 0,
                    "max_risk_score": 0.0,
                    "scores": [],
                    "last_seen": ts,
                    "related_incident_ids": [],
                },
            )

            entry["occurrences"] += 1
            entry["related_incident_ids"].append(incident_id)
            entry["max_risk_score"] = max(entry["max_risk_score"], risk_score)
            entry["last_seen"] = max(entry["last_seen"], ts)
            entry["scores"].append((risk_score, severity))

    results: List[IdentityAggregateItemV1] = []
    for email, data in buckets.items():
        highest_severity = _severity_for_max_score(data["scores"])
        results.append(
            IdentityAggregateItemV1(
                email=data["email"],
                domain=data["domain"],
                occurrences=data["occurrences"],
                max_risk_score=int(round(data["max_risk_score"])),
                highest_severity=highest_severity,
                last_seen=data["last_seen"],
                related_incident_ids=data["related_incident_ids"],
            )
        )

    results.sort(key=lambda item: item.occurrences, reverse=True)
    return results


@app.get("/metrics", response_model=MetricsResponseV1)
def get_metrics() -> MetricsResponseV1:
    """
    Aggregate metrics from the latest scan results.
    """
    incidents = list(_INCIDENT_STORE.values())
    counts = {
        Severity.CRITICAL: 0,
        Severity.HIGH: 0,
        Severity.MEDIUM: 0,
        Severity.LOW: 0,
    }

    for inc in incidents:
        sev = _normalize_severity(inc.get("severity"))
        counts[sev] += 1

    return MetricsResponseV1(
        total=len(incidents),
        critical=counts[Severity.CRITICAL],
        high=counts[Severity.HIGH],
        medium=counts[Severity.MEDIUM],
        low=counts[Severity.LOW],
    )


@app.get("/incidents", response_model=List[IncidentSummaryV1])
def list_incidents() -> List[IncidentSummaryV1]:
    """
    Table view of incidents. Does not expose full raw text or entities.
    """
    summaries: List[IncidentSummaryV1] = []
    for inc in _INCIDENT_STORE.values():
        entities = inc.get("entities") or []
        timestamp = _parse_timestamp(inc.get("timestamp") or _LAST_SCAN_TIMESTAMP)

        summaries.append(
            IncidentSummaryV1(
                incident_id=str(inc.get("incident_id")),
                source=str(inc.get("source") or ""),
                timestamp=timestamp,
                severity=_normalize_severity(inc.get("severity")),
                risk_score=int(round(float(inc.get("risk_score", 0.0)))),
                entity_count=len(entities),
            )
        )

    # Sort newest first for UX
    summaries.sort(key=lambda s: s.timestamp, reverse=True)
    return summaries


@app.get("/incidents/{incident_id}", response_model=IncidentDetailV1)
def get_incident_detail(incident_id: str) -> IncidentDetailV1:
    """
    Detailed incident view suitable for the frontend detail panel.
    """
    if incident_id not in _INCIDENT_STORE:
        raise HTTPException(status_code=404, detail="Incident not found")

    inc = _INCIDENT_STORE[incident_id]
    entities_raw = inc.get("entities") or []

    entities: List[IncidentEntityV1] = []
    for ent in entities_raw:
        # Ensure we only ever expose masked values & normalized methods.
        entities.append(
            IncidentEntityV1(
                type=str(ent.get("type") or ""),
                masked_value=str(ent.get("masked_value") or ""),
                confidence=float(ent.get("confidence") or 0.0),
                detection_method=_to_detection_method(ent.get("detection_method")),
            )
        )

    timestamp = _parse_timestamp(inc.get("timestamp") or _LAST_SCAN_TIMESTAMP)

    return IncidentDetailV1(
        incident_id=str(inc.get("incident_id")),
        source=str(inc.get("source") or ""),
        url=str(inc.get("url") or ""),
        timestamp=timestamp,
        severity=_normalize_severity(inc.get("severity")),
        risk_score=int(round(float(inc.get("risk_score", 0.0)))),
        entities=entities,
        context_snippet=str(inc.get("context_snippet") or ""),
    )


@app.get("/identities", response_model=List[IdentityAggregateItemV1])
def list_identities() -> List[IdentityAggregateItemV1]:
    """
    Identity-centric aggregation endpoint.

    Groups incidents by EMAIL entities and exposes summary stats.
    """
    incidents = list(_INCIDENT_STORE.values())
    return aggregate_identities(incidents)
