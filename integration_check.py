"""
Minimal integration script for STRIDER.

Run:
    python integration_check.py

This will:
1. Load scraped documents from `config.OUTPUT_FILE` if present,
   otherwise use a small synthetic document.
2. Execute the full detection -> classification -> risk scoring pipeline.
3. Print a short summary of incidents to stdout.
"""

from __future__ import annotations

import json
from pathlib import Path

import config
from backend.pipeline import run_pipeline
from utils.schema import create_document
from utils.logger import get_logger


logger = get_logger("integration_check")


def main() -> None:
    output_path = Path(config.OUTPUT_FILE)
    if output_path.exists():
        logger.info(f"Loading scraped documents from {output_path}")
        with output_path.open("r", encoding="utf-8") as f:
            documents = json.load(f)
        if not isinstance(documents, list):
            logger.warning("Scraped document file did not contain a list; using empty list")
            documents = []
    else:
        logger.info("No scraped documents found; using synthetic test document")
        documents = [
            create_document(
                source="synthetic",
                source_type="unit",
                url="https://example.com",
                raw_text="Contact me at test@example.com or +1 123-456-7890.",
                clean_text="Contact me at test@example.com or +1 123-456-7890.",
                author="tester",
                tags=["synthetic"],
            )
        ]

    incidents = run_pipeline(documents)
    print(f"Incidents produced: {len(incidents)}")
    for inc in incidents:
        print(
            f"- {inc.get('incident_id')}: "
            f"severity={inc.get('severity')}, "
            f"risk_score={inc.get('risk_score')}, "
            f"entities={len(inc.get('entities') or [])}"
        )


if __name__ == "__main__":
    main()

