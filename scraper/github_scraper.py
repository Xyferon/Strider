"""
GitHub Code Search scraper.
Searches for PII-related keywords, fetches raw file contents,
applies rate limiting and exponential backoff.
"""

import time
import requests
import config
from utils.logger import get_logger
from scraper.cleaner import clean_text
from utils.schema import create_document
from utils.rate_limiter import RateLimiter

logger = get_logger("github_scraper")

GITHUB_API_SEARCH = "https://api.github.com/search/code"
GITHUB_API_BASE = "https://api.github.com"


def _build_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PII-Leakage-Scanner/1.0",
    }
    if config.GITHUB_TOKEN:
        token = config.GITHUB_TOKEN.strip()
        # GitHub classic PATs typically use `token ...`; fine-grained PATs use `Bearer ...`.
        if token.startswith("github_pat_"):
            headers["Authorization"] = f"Bearer {token}"
        else:
            headers["Authorization"] = f"token {token}"
    return headers


def _fetch_raw_content(url: str, headers: dict, limiter: RateLimiter) -> str | None:
    """
    Fetch the raw text content of a GitHub file.
    Returns None on failure.
    """
    for attempt in range(config.GITHUB_BACKOFF_MAX_RETRIES + 1):
        limiter.wait_if_needed()
        try:
            resp = requests.get(url, headers=headers, timeout=15)

            if resp.status_code == 200:
                return resp.text

            if resp.status_code in (403, 429):
                wait = limiter.handle_rate_limit_response(resp)
                if wait:
                    time.sleep(wait)
                if not limiter.backoff(attempt):
                    return None
                continue

            logger.warning(f"Unexpected status {resp.status_code} for {url}")
            return None

        except requests.RequestException as exc:
            logger.error(f"Request error for {url}: {exc}")
            if not limiter.backoff(attempt):
                return None

    return None


def _search_code(keyword: str, headers: dict, limiter: RateLimiter) -> list[dict]:
    """
    Search GitHub code for a keyword.  Returns list of search-result items.
    """
    items: list[dict] = []
    params = {
        "q": keyword,
        "per_page": min(config.GITHUB_RESULTS_PER_KEYWORD, 30),
    }

    for attempt in range(config.GITHUB_BACKOFF_MAX_RETRIES + 1):
        limiter.wait_if_needed()
        try:
            resp = requests.get(
                GITHUB_API_SEARCH, headers=headers, params=params, timeout=15
            )

            if resp.status_code == 200:
                data = resp.json()
                items = data.get("items", [])
                total = data.get("total_count", 0)
                logger.info(
                    f"Search '{keyword}': {len(items)} items (total_count={total})"
                )
                return items

            if resp.status_code in (403, 429):
                if not config.GITHUB_TOKEN and resp.status_code == 403:
                    logger.warning("Unauthenticated rate limit hit. Failing fast.")
                    return []
                
                wait = limiter.handle_rate_limit_response(resp)
                if wait:
                    time.sleep(wait)
                if not limiter.backoff(attempt):
                    return []
                continue

            if resp.status_code == 422:
                logger.warning(f"Validation error for keyword '{keyword}': {resp.text}")
                return []

            logger.warning(
                f"Search failed for '{keyword}': status {resp.status_code}"
            )
            return []

        except requests.RequestException as exc:
            logger.error(f"Search request error for '{keyword}': {exc}")
            if not limiter.backoff(attempt):
                return []

    return []


from concurrent.futures import ThreadPoolExecutor, as_completed

def _process_github_item(item: dict, keyword: str, headers: dict, limiter: RateLimiter) -> dict | None:
    """Worker function to process a single GitHub search result item."""
    try:
        html_url = item.get("html_url", "")
        repo_data = item.get("repository") or {}
        repo_full = repo_data.get("full_name", "")
        file_path = item.get("path", "")
        file_name = item.get("name", "")

        # Build raw content URL
        raw_url = html_url.replace(
            "github.com", "raw.githubusercontent.com"
        ).replace("/blob/", "/")

        if not raw_url:
            return None

        # Check file size via API if available
        size = item.get("size", 0)
        if size and size > config.GITHUB_MAX_FILE_SIZE_BYTES:
            logger.info(f"Skipping large file ({size} bytes): {file_path}")
            return None

        # Fetch raw content
        raw_text = _fetch_raw_content(raw_url, headers, limiter)
        if raw_text is None:
            return None

        # Skip empty or binary-looking content
        if not raw_text.strip():
            logger.info(f"Skipping empty file: {file_path}")
            return None

        # Check size after download
        if len(raw_text.encode("utf-8", errors="replace")) > config.GITHUB_MAX_FILE_SIZE_BYTES:
            logger.info(f"Skipping oversized content: {file_path}")
            return None

        # Simple binary check — high ratio of null-ish bytes
        if "\x00" in raw_text[:1024]:
            logger.info(f"Skipping binary file: {file_path}")
            return None

        cleaned = clean_text(raw_text)

        # Detect language from file extension
        ext = file_name.rsplit(".", 1)[-1] if "." in file_name else None

        owner_data = repo_data.get("owner") or {}
        author = owner_data.get("login")

        doc = create_document(
            source="github",
            source_type="code",
            url=html_url,
            raw_text=raw_text,
            clean_text=cleaned,
            author=author,
            repository=repo_full,
            language=ext,
            tags=[keyword],
        )
        return doc

    except Exception as exc:
        logger.error(f"Error processing GitHub item: {exc}")
        return None

def scrape_github() -> list[dict]:
    """
    Main entry point.  Searches GitHub for PII-related keywords,
    fetches raw file contents concurrently, and returns schema-compliant documents.
    """
    if not config.GITHUB_TOKEN:
        logger.warning(
            "GITHUB_TOKEN not set. GitHub scraping will likely hit "
            "unauthenticated rate limits very quickly."
        )

    headers = _build_headers()
    limiter = RateLimiter(
        max_requests=config.GITHUB_MAX_REQUESTS_PER_MINUTE,
        window_seconds=config.GITHUB_RATE_WINDOW_SECONDS,
        backoff_base=config.GITHUB_BACKOFF_BASE_SECONDS,
        max_retries=config.GITHUB_BACKOFF_MAX_RETRIES,
    )

    documents: list[dict] = []

    for keyword in config.GITHUB_SEARCH_KEYWORDS:
        logger.info(f"Searching GitHub for: '{keyword}'")
        items = _search_code(keyword, headers, limiter)
        
        # Process items concurrently using ThreadPoolExecutor
        if not items:
            continue
            
        logger.info(f"Processing {len(items)} items for '{keyword}' concurrently...")
        with ThreadPoolExecutor(max_workers=10) as executor:
            future_to_item = {
                executor.submit(_process_github_item, item, keyword, headers, limiter): item
                for item in items
            }
            
            for future in as_completed(future_to_item):
                doc = future.result()
                if doc:
                    documents.append(doc)

    logger.info(f"GitHub scraping complete. Collected {len(documents)} documents.")
    return documents
