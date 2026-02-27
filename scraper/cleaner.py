"""
Text cleaning pipeline.
Strips HTML, removes scripts/styles, decodes escapes, normalizes whitespace,
removes null bytes, ensures UTF-8.  Preserves numbers, emails, identifiers.
"""

import re
import html as html_module
from bs4 import BeautifulSoup


def clean_text(raw: str) -> str:
    """
    Clean raw text for the detection engine.

    Steps:
        1. Remove <script> and <style> blocks
        2. Strip all remaining HTML tags
        3. Decode HTML entities (&amp; → &)
        4. Remove null bytes
        5. Normalize whitespace (collapse runs, strip)
        6. Ensure valid UTF-8

    Numbers, emails, and identifiers are intentionally preserved.
    """
    if not raw:
        return ""

    text = raw

    # 1. Remove <script> and <style> blocks (case-insensitive)
    text = re.sub(
        r"<script[\s\S]*?</script>", "", text, flags=re.IGNORECASE
    )
    text = re.sub(
        r"<style[\s\S]*?</style>", "", text, flags=re.IGNORECASE
    )

    # 2. Strip remaining HTML tags using BeautifulSoup for robustness
    if "<" in text and ">" in text:
        soup = BeautifulSoup(text, "html.parser")
        text = soup.get_text(separator=" ")

    # 3. Decode HTML entities
    text = html_module.unescape(text)

    # 4. Remove null bytes
    text = text.replace("\x00", "")

    # 5. Normalize whitespace — collapse runs of spaces/tabs, keep newlines
    text = re.sub(r"[^\S\n]+", " ", text)          # horizontal whitespace → single space
    text = re.sub(r"\n{3,}", "\n\n", text)         # 3+ newlines → 2
    text = text.strip()

    # 6. Ensure valid UTF-8
    text = text.encode("utf-8", errors="replace").decode("utf-8")

    return text
