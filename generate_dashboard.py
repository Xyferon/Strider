"""
Generate a static HTML dashboard from the latest incidents.

Run:
    python app.py                 # collect + deduplicate documents
    python generate_dashboard.py  # build reports/dashboard.html
"""

from __future__ import annotations

import json
from pathlib import Path

import config
from backend.pipeline import run_pipeline
from reports.dashboard import Dashboard
from utils.logger import get_logger


import argparse

logger = get_logger("generate_dashboard")


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate PII Dashboard")
    parser.add_argument("--domain", type=str, help="Target domain or keyword to filter report generation.")
    args = parser.parse_args()

    output_path = Path(config.OUTPUT_FILE)
    if not output_path.exists():
        logger.warning("No scraped documents found; run `python app.py` first.")
        documents = []
    else:
        with output_path.open("r", encoding="utf-8") as f:
            documents = json.load(f)
        if not isinstance(documents, list):
            logger.error("Scraped document file did not contain a list; using empty list")
            documents = []

    incidents = run_pipeline(documents, target=args.domain)

    dashboard = Dashboard()
    html = dashboard.render(incidents)

    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    out_file = reports_dir / "dashboard.html"
    out_file.write_text(html, encoding="utf-8")

    logger.info(f"Dashboard written to {out_file.resolve()}")
    print(f"Dashboard written to {out_file.resolve()}")


if __name__ == "__main__":
    main()

