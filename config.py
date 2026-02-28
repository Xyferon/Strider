"""
Central configuration for the STRIDER / PII Leakage Scanner project.

All modules must import settings from this file using absolute imports:

    import config

Environment variables can override sane defaults for demo use.
"""

from __future__ import annotations

import os
from pathlib import Path


# ---- Paths -----------------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
CLEAN_DATA_DIR = DATA_DIR / "cleaned"

OUTPUT_DIR = RAW_DATA_DIR
OUTPUT_FILE = OUTPUT_DIR / "scraped_documents.json"


# ---- GitHub Scraper --------------------------------------------------------

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()

GITHUB_SEARCH_KEYWORDS = [
    "password",
    "token",
    "secret",
    "credentials",
]

GITHUB_RESULTS_PER_KEYWORD = int(os.getenv("GITHUB_RESULTS_PER_KEYWORD", "10"))
GITHUB_MAX_REQUESTS_PER_MINUTE = int(os.getenv("GITHUB_MAX_REQUESTS_PER_MINUTE", "20"))
GITHUB_RATE_WINDOW_SECONDS = int(os.getenv("GITHUB_RATE_WINDOW_SECONDS", "60"))

GITHUB_BACKOFF_BASE_SECONDS = float(os.getenv("GITHUB_BACKOFF_BASE_SECONDS", "2.0"))
GITHUB_BACKOFF_MAX_RETRIES = int(os.getenv("GITHUB_BACKOFF_MAX_RETRIES", "3"))

GITHUB_MAX_FILE_SIZE_BYTES = int(os.getenv("GITHUB_MAX_FILE_SIZE_BYTES", str(200_000)))


# ---- Pastebin Scraper ------------------------------------------------------

PASTEBIN_ARCHIVE_URL = os.getenv(
    "PASTEBIN_ARCHIVE_URL",
    "https://pastebin.com/archive",
)
PASTEBIN_RAW_URL_TEMPLATE = os.getenv(
    "PASTEBIN_RAW_URL_TEMPLATE",
    "https://pastebin.com/raw/{paste_id}",
)

PASTEBIN_MAX_PASTES = int(os.getenv("PASTEBIN_MAX_PASTES", "10"))

PASTEBIN_DELAY_MIN = float(os.getenv("PASTEBIN_DELAY_MIN", "0.5"))
PASTEBIN_DELAY_MAX = float(os.getenv("PASTEBIN_DELAY_MAX", "1.5"))
PASTEBIN_JITTER = float(os.getenv("PASTEBIN_JITTER", "3.0"))


__all__ = [
    "PROJECT_ROOT",
    "DATA_DIR",
    "RAW_DATA_DIR",
    "CLEAN_DATA_DIR",
    "OUTPUT_DIR",
    "OUTPUT_FILE",
    "GITHUB_TOKEN",
    "GITHUB_SEARCH_KEYWORDS",
    "GITHUB_RESULTS_PER_KEYWORD",
    "GITHUB_MAX_REQUESTS_PER_MINUTE",
    "GITHUB_RATE_WINDOW_SECONDS",
    "GITHUB_BACKOFF_BASE_SECONDS",
    "GITHUB_BACKOFF_MAX_RETRIES",
    "GITHUB_MAX_FILE_SIZE_BYTES",
    "PASTEBIN_ARCHIVE_URL",
    "PASTEBIN_RAW_URL_TEMPLATE",
    "PASTEBIN_MAX_PASTES",
    "PASTEBIN_DELAY_MIN",
    "PASTEBIN_DELAY_MAX",
    "PASTEBIN_JITTER",
]

