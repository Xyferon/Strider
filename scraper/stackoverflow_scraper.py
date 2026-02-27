"""
StackOverflow Recent Posts scraper.
Fetches the absolute newest questions from StackOverflow via the StackExchange API.
These posts often contain raw code, configurations, and stack traces with PII.
Generous rate limits and no authentication required.
"""

import time
import requests
import config
from utils.logger import get_logger
from scraper.cleaner import clean_text
from utils.schema import create_document
from utils.rate_limiter import RateLimiter

logger = get_logger("stackoverflow_scraper")

STACK_EXCHANGE_API = "https://api.stackexchange.com/2.3/questions"

def scrape_stackoverflow() -> list[dict]:
    """
    Scrapes the most recent 30 questions on StackOverflow that contain body text.
    """
    logger.info("Starting StackOverflow scraper...")
    documents: list[dict] = []
    
    # Simple limiter: max 10 requests per minute to be extremely safe, though API allows 300/day unauthenticated.
    limiter = RateLimiter(
        max_requests=10, 
        window_seconds=60,
        backoff_base=2.0,
        max_retries=3
    )
    
    params = {
        "order": "desc",
        "sort": "creation",
        "site": "stackoverflow",
        "filter": "withbody",  # Ensures we get the body markdown/html
        "pagesize": 30
    }
    
    limiter.wait_if_needed()
    try:
        resp = requests.get(STACK_EXCHANGE_API, params=params, timeout=15)
        
        if resp.status_code == 200:
            data = resp.json()
            items = data.get("items", [])
            logger.info(f"Retrieved {len(items)} recent StackOverflow questions.")
            
            for item in items:
                raw_text = item.get("body_markdown", "") or item.get("body", "")
                
                # Skip if there's hardly any text
                if len(raw_text) < 50:
                    continue
                    
                cleaned = clean_text(raw_text)
                owner = item.get("owner", {})
                author = owner.get("display_name", "Unknown")
                
                doc = create_document(
                    source="stackoverflow",
                    source_type="forum_post",
                    url=item.get("link", ""),
                    raw_text=raw_text,
                    clean_text=cleaned,
                    author=author,
                    tags=["stackoverflow", "code"]
                )
                
                timestamp = item.get("creation_date")
                if timestamp:
                    # Convert unix epoch to ISO
                    from datetime import datetime, timezone
                    doc["timestamp"] = datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
                    
                documents.append(doc)
                
        elif resp.status_code == 429:
            logger.warning("StackExchange API rate limit hit.")
        else:
            logger.warning(f"StackExchange API returned status {resp.status_code}: {resp.text}")
            
    except requests.RequestException as exc:
        logger.error(f"StackOverflow Request error: {exc}")
        
    logger.info(f"StackOverflow scraping complete. Collected {len(documents)} documents.")
    return documents

if __name__ == "__main__":
    docs = scrape_stackoverflow()
    for d in docs[:3]:
        print(d["url"], "->", len(d["clean_text"]), "chars")
