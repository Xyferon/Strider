"""
GitHub Public Gists Scraper.
Constantly fetches the latest public gists from GitHub.
Gists are frequently used to share logs, secrets, and database extracts.
"""

import time
import requests
import config
from utils.logger import get_logger
from scraper.cleaner import clean_text
from utils.schema import create_document
from utils.rate_limiter import RateLimiter

logger = get_logger("gist_scraper")

GITHUB_GIST_API = "https://api.github.com/gists/public"

def _build_headers() -> dict:
    headers = {
        "Accept": "application/vnd.github.v3+json",
        "User-Agent": "PII-Leakage-Scanner/1.0",
    }
    if config.GITHUB_TOKEN:
        token = config.GITHUB_TOKEN.strip()
        if token.startswith("github_pat_"):
            headers["Authorization"] = f"Bearer {token}"
        else:
            headers["Authorization"] = f"token {token}"
        logger.info("Using authenticated GitHub token for Gists.")
    else:
        logger.info("Using unauthenticated GitHub requests for Gists.")
    return headers

def scrape_gists() -> list[dict]:
    """
    Main entry point. Fetches recent public gists and pulls raw file contents.
    """
    logger.info("Starting GitHub Gist scraping...")
    headers = _build_headers()
    limiter = RateLimiter(
        max_requests=config.GITHUB_MAX_REQUESTS_PER_MINUTE,
        window_seconds=config.GITHUB_RATE_WINDOW_SECONDS,
        backoff_base=config.GITHUB_BACKOFF_BASE_SECONDS,
        max_retries=config.GITHUB_BACKOFF_MAX_RETRIES
    )

    documents: list[dict] = []
    
    limiter.wait_if_needed()
    try:
        resp = requests.get(GITHUB_GIST_API, headers=headers, params={"per_page": 30}, timeout=15)
        
        if resp.status_code == 200:
            items = resp.json()
            logger.info(f"Retrieved {len(items)} recent public gists.")
            
            for item in items:
                # Gists can contain multiple files
                files = item.get("files", {})
                gist_url = item.get("html_url", "")
                author = item.get("owner", {}).get("login", "Anonymous")
                created_at = item.get("created_at")
                
                for filename, filedata in files.items():
                    raw_url = filedata.get("raw_url")
                    if not raw_url:
                        continue
                    
                    # Size check to avoid freezing up (skip > 1MB)
                    size = filedata.get("size", 0)
                    if size > 1000 * 1024:
                        logger.info(f"Skipping exceptionally large gist file ({size} bytes).")
                        continue
                    
                    # Fetch raw file
                    limiter.wait_if_needed()
                    try:
                        f_resp = requests.get(raw_url, timeout=10)
                        if f_resp.status_code == 200:
                            raw_text = f_resp.text
                            
                            if len(raw_text) < 20:
                                continue # Too small to contain PII
                                
                            cleaned = clean_text(raw_text)
                            
                            doc = create_document(
                                source="gist",
                                source_type="code_snippet",
                                url=gist_url,
                                raw_text=raw_text,
                                clean_text=cleaned,
                                author=author,
                                tags=["gist", "public"]
                            )
                            
                            if created_at:
                                doc["timestamp"] = created_at
                                
                            documents.append(doc)
                            
                    except requests.RequestException:
                        continue # Ignore individual file failures
                        
        elif resp.status_code == 403 or resp.status_code == 429:
            logger.warning("GitHub Gist API rate limit hit.")
        else:
            logger.warning(f"Gist API returned status {resp.status_code}.")

    except requests.RequestException as exc:
        logger.error(f"Gist Request error: {exc}")

    logger.info(f"GitHub Gist scraping complete. Collected {len(documents)} documents.")
    return documents

if __name__ == "__main__":
    docs = scrape_gists()
    for d in docs[:3]:
        print(d["url"], "->", len(d["clean_text"]), "chars")
