"""
PII Leakage Scanner — Main Application
================================================
Main orchestrator. Runs all scrapers, deduplicates, and writes
the final JSON output for the Detection Engine.

Usage:
    python app.py
"""

import os
import sys
import json
import time
import argparse
import config
from utils.logger import get_logger
from utils.dedup import Deduplicator
from scraper.github_scraper import scrape_github
from scraper.pastebin_scraper import scrape_pastebin
from scraper.social_scraper import scrape_social_media
from scraper.stackoverflow_scraper import scrape_stackoverflow
from scraper.gist_scraper import scrape_gists

logger = get_logger("main")


def run_full_scan(domain: str = None) -> list[dict]:
    start = time.time()
    logger.info("=" * 60)
    logger.info("PII Leakage Scanner - Data Acquisition Layer")
    if domain:
        logger.info(f"Targeting specific domain/keyword: {domain}")
    logger.info("=" * 60)

    all_documents: list[dict] = []

    # 1. GitHub Scraper
    logger.info("--- Phase 1: GitHub Scraping ---")
    try:
        github_docs = scrape_github()
        all_documents.extend(github_docs)
        logger.info(f"GitHub: {len(github_docs)} documents collected")
    except Exception as exc:
        logger.error(f"GitHub scraper crashed: {exc}")

    # 2. Pastebin Scraper
    logger.info("--- Phase 2: Pastebin Scraping ---")
    try:
        pastebin_docs = scrape_pastebin()
        all_documents.extend(pastebin_docs)
        logger.info(f"Pastebin: {len(pastebin_docs)} documents collected")
    except Exception as exc:
        logger.error(f"Pastebin scraper crashed: {exc}")

    # 3. Social Media Scraper
    logger.info("--- Phase 3: Social Media Scraping ---")
    logger.info("Social media scraping is currently disabled (mock data removed).")

    # 4. StackOverflow Scraper
    logger.info("--- Phase 4: StackOverflow Scraping ---")
    try:
        so_docs = scrape_stackoverflow()
        all_documents.extend(so_docs)
        logger.info(f"StackOverflow: {len(so_docs)} documents collected")
    except Exception as exc:
        logger.error(f"StackOverflow scraper crashed: {exc}")

    # 5. GitHub Gists Scraper
    logger.info("--- Phase 5: GitHub Gists Scraping ---")
    try:
        gist_docs = scrape_gists()
        all_documents.extend(gist_docs)
        logger.info(f"GitHub Gists: {len(gist_docs)} documents collected")
    except Exception as exc:
        logger.error(f"GitHub Gists scraper crashed: {exc}")

    # 6. Deduplication & Filtering
    logger.info("--- Phase 6: Deduplication & Filtering ---")
    dedup = Deduplicator()
    unique_documents: list[dict] = []

    duplicates = 0
    filtered = 0
    for doc in all_documents:
        # Pre-filter by domain if specified
        if domain:
            t = domain.lower()
            url = str(doc.get("url") or "").lower()
            raw_text = str(doc.get("raw_text") or "").lower()
            clean_text = str(doc.get("clean_text") or "").lower()
            if t not in url and t not in raw_text and t not in clean_text:
                filtered += 1
                continue
                
        if dedup.is_duplicate(doc["clean_text"]):
            duplicates += 1
        else:
            unique_documents.append(doc)

    logger.info(
        f"Deduplication: {duplicates} duplicates removed, {filtered} filtered out by domain match. "
        f"{len(unique_documents)} unique documents remain"
    )

    # ── 5. Write Output ────────────────────────────────────────────────
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    with open(config.OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(unique_documents, f, indent=2, ensure_ascii=False)

    elapsed = time.time() - start

    # Summary
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
    
    return unique_documents


def main():
    parser = argparse.ArgumentParser(description="Strider - PII Leakage Scanner")
    parser.add_argument("--domain", type=str, help="Target domain or keyword to filter scraping results.")
    args = parser.parse_args()
    run_full_scan(args.domain)


if __name__ == "__main__":
    main()
