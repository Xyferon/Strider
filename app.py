"""
PII Leakage Scanner — Main Application
================================================
Main orchestrator. Runs all scrapers, deduplicates, and writes
the final JSON output for the Detection Engine.

Usage:
    python app.py
"""

import os
import json
import time
import config
from utils.logger import get_logger
from utils.dedup import Deduplicator
from scraper.github_scraper import scrape_github
from scraper.pastebin_scraper import scrape_pastebin

logger = get_logger("main")


def main():
    start = time.time()
    logger.info("=" * 60)
    logger.info("PII Leakage Scanner — Data Acquisition Layer")
    logger.info("=" * 60)

    all_documents: list[dict] = []

    # ── 1. GitHub Scraper ───────────────────────────────────────────────
    logger.info("─── Phase 1: GitHub Scraping ───")
    try:
        github_docs = scrape_github()
        all_documents.extend(github_docs)
        logger.info(f"GitHub: {len(github_docs)} documents collected")
    except Exception as exc:
        logger.error(f"GitHub scraper crashed: {exc}")

    # ── 2. Pastebin Scraper ─────────────────────────────────────────────
    logger.info("─── Phase 2: Pastebin Scraping ───")
    try:
        pastebin_docs = scrape_pastebin()
        all_documents.extend(pastebin_docs)
        logger.info(f"Pastebin: {len(pastebin_docs)} documents collected")
    except Exception as exc:
        logger.error(f"Pastebin scraper crashed: {exc}")

    # ── 3. Deduplication ────────────────────────────────────────────────
    logger.info("─── Phase 3: Deduplication ───")
    dedup = Deduplicator()
    unique_documents: list[dict] = []

    duplicates = 0
    for doc in all_documents:
        if dedup.is_duplicate(doc["clean_text"]):
            duplicates += 1
        else:
            unique_documents.append(doc)

    logger.info(
        f"Deduplication: {duplicates} duplicates removed, "
        f"{len(unique_documents)} unique documents remain"
    )

    # ── 4. Write Output ────────────────────────────────────────────────
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_documents, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start

    # ── Summary ─────────────────────────────────────────────────────────
    logger.info("=" * 60)
    logger.info("SUMMARY")
    logger.info(f"  Total collected  : {len(all_documents)}")
    logger.info(f"  Duplicates       : {duplicates}")
    logger.info(f"  Unique output    : {len(unique_documents)}")
    logger.info(f"  Output file      : {config.OUTPUT_FILE}")
    logger.info(f"  Elapsed time     : {elapsed:.1f}s")
    logger.info("=" * 60)

    # Use ASCII-only output for Windows consoles that default to cp1252.
    print(f"\nDone. {len(unique_documents)} documents -> {config.OUTPUT_FILE}")
    print(f"Time: {elapsed:.1f}s")


if __name__ == "__main__":
    main()
