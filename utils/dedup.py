"""
Simple content-based deduplication utilities.

Used by `app.py` to prevent processing the same document multiple times.
"""

from __future__ import annotations

import hashlib
from typing import Set


class Deduplicator:
    def __init__(self) -> None:
        self._seen_hashes: Set[str] = set()

    def _hash(self, text: str) -> str:
        data = (text or "").encode("utf-8", errors="ignore")
        return hashlib.sha256(data).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        """
        Return True if the given text has been seen before.
        """
        key = self._hash(text)
        if key in self._seen_hashes:
            return True
        self._seen_hashes.add(key)
        return False


__all__ = ["Deduplicator"]

