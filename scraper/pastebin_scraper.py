"""
Pastebin archive scraper.
Fetches recent pastes from the public archive, retrieves raw content,
rate-limits aggressively to avoid bans.
"""

import re
import requests
import config
from utils.logger import get_logger
from scraper.cleaner import clean_text
from utils.schema import create_document
from utils.rate_limiter import PastebinRateLimiter

logger = get_logger("pastebin_scraper")


def _get_paste_ids() -> list[str]:
    """
    Scrape the Pastebin archive page for paste IDs.
    Returns a list of paste ID strings.
    """
    try:
        resp = requests.get(
            config.PASTEBIN_ARCHIVE_URL,
            headers={"User-Agent": "PII-Leakage-Scanner/1.0"},
            timeout=15,
        )
        if resp.status_code != 200:
            logger.warning(f"Archive page returned status {resp.status_code}")
            return []

        # Extract paste IDs from archive links.
        # Pastebin currently uses links like: href="/aEmhHhEi?source=archive"
        paste_ids = re.findall(
            r'href="/([A-Za-z0-9]{8})(?:\?[^"]*)?"',
            resp.text,
        )

        # Deduplicate while preserving order
        seen = set()
        unique_ids = []
        for pid in paste_ids:
            if pid not in seen:
                seen.add(pid)
                unique_ids.append(pid)

        logger.info(f"Found {len(unique_ids)} paste IDs on archive page")
        return unique_ids[: config.PASTEBIN_MAX_PASTES]

    except requests.RequestException as exc:
        logger.error(f"Failed to fetch archive page: {exc}")
        return []


def scrape_pastebin() -> list[dict]:
    """
    Main entry point.  Fetches recent Pastebin pastes and returns
    schema-compliant documents.
    """
    limiter = PastebinRateLimiter(
        min_delay=config.PASTEBIN_DELAY_MIN,
        max_delay=config.PASTEBIN_DELAY_MAX,
        jitter=config.PASTEBIN_JITTER,
    )

    paste_ids = _get_paste_ids()
    if not paste_ids:
        logger.warning("No paste IDs found. Skipping Pastebin scraping.")
        return []

    documents: list[dict] = []

    for i, paste_id in enumerate(paste_ids):
        raw_url = config.PASTEBIN_RAW_URL_TEMPLATE.format(paste_id=paste_id)
        html_url = f"https://pastebin.com/{paste_id}"

        try:
            limiter.wait()
            resp = requests.get(
                raw_url,
                headers={"User-Agent": "PII-Leakage-Scanner/1.0"},
                timeout=15,
            )

            if resp.status_code != 200:
                logger.warning(
                    f"Paste {paste_id}: status {resp.status_code}"
                )
                continue

            raw_text = resp.text

            if not raw_text.strip():
                logger.info(f"Paste {paste_id}: empty, skipping")
                continue

            # Skip very large pastes
            if len(raw_text.encode("utf-8", errors="replace")) > config.GITHUB_MAX_FILE_SIZE_BYTES:
                logger.info(f"Paste {paste_id}: too large, skipping")
                continue

            cleaned = clean_text(raw_text)

            doc = create_document(
                source="pastebin",
                source_type="paste",
                url=html_url,
                raw_text=raw_text,
                clean_text=cleaned,
                author=None,
                tags=["archive"],
            )
            documents.append(doc)
            logger.info(
                f"Paste {i + 1}/{len(paste_ids)}: {paste_id} collected "
                f"({len(cleaned)} chars)"
            )

        except requests.RequestException as exc:
            logger.error(f"Paste {paste_id}: request error — {exc}")
            continue
        except Exception as exc:
            logger.error(f"Paste {paste_id}: unexpected error — {exc}")
            continue

    logger.info(
        f"Pastebin scraping complete. Collected {len(documents)} documents."
    )
    return documents
