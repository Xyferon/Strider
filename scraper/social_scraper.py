"""
Social media scraper module (mock).
Scrapes simulated social media platforms since Reddit API is unavailable.
"""

from typing import List, Dict, Any
import time

from utils.logger import get_logger
from utils.schema import create_document

logger = get_logger("social_scraper")


def scrape_social_media() -> List[Dict[str, Any]]:
    """
    Mock scraping social media sources (e.g., Mastodon or dummy Twitter).
    
    Returns:
        List of documents adhering to the common schema.
    """
    import random
    import uuid
    import datetime

    logger.info("Starting social media mock scraping (Randomized Generation)")
    
    # Generate 5 to 10 random mock posts
    num_posts = random.randint(5, 10)
    documents = []
    
    first_names = ["Emma", "Noah", "Olivia", "Liam", "Ava", "William", "Sophia", "Mason", "Isabella", "James"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis", "Rodriguez", "Martinez"]
    companies = ["Acme Corp", "TechGlobal", "Initech", "Globex", "Soylent Corp"]
    
    for _ in range(num_posts):
        fname = random.choice(first_names)
        lname = random.choice(last_names)
        company = random.choice(companies)
        
        # Decide what PII to leak
        leak_type = random.choice(["credit_card", "phone", "email", "aadhaar"])
        
        post_content = f"Hey everyone! I'm {fname} {lname} and I work at {company}. "
        
        if leak_type == "credit_card":
            cc = f"4111 {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
            post_content += f"I just got my new company card, look at it: {cc}!!"
        elif leak_type == "phone":
            phone = f"{random.randint(200,999)}-{random.randint(200,999)}-{random.randint(1000,9999)}"
            post_content += f"Call me at my new number: {phone}"
        elif leak_type == "email":
            email = f"{fname.lower()}.{lname.lower()}{random.randint(1,99)}@{company.lower().replace(' ', '')}.com"
            post_content += f"Shoot me an email at {email} if you need anything."
        elif leak_type == "aadhaar":
            aadhaar = f"{random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000,9999)}"
            post_content += f"Is it safe to share my Aadhaar? It's {aadhaar}."
            
        timestamp = (datetime.datetime.utcnow() - datetime.timedelta(minutes=random.randint(1, 1000))).isoformat() + "Z"
        
        doc = create_document(
            source="social_media",
            source_type="social",
            url=f"https://social.dummy.local/post/{uuid.uuid4().hex[:8]}",
            raw_text=post_content,
            clean_text=post_content,
            author=f"@{fname.lower()}{lname.lower()}{random.randint(10,99)}",
            tags=["mock", "social", leak_type]
        )
        doc["timestamp"] = timestamp
        documents.append(doc)
        
    time.sleep(0.5)  # Simulate network delay
    logger.info(f"Social media scraping complete. Collected {len(documents)} randomized mockup posts.")
    return documents

if __name__ == "__main__":
    docs = scrape_social_media()
    for d in docs:
        print(d["url"], "->", d["clean_text"])
