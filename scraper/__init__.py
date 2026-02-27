"""
Scraper module for data collection.
"""

from scraper.github_scraper import scrape_github
from scraper.pastebin_scraper import scrape_pastebin
from scraper.cleaner import clean_text

__all__ = ["scrape_github", "scrape_pastebin", "clean_text"]
