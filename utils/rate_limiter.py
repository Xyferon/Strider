"""
Rate limiting helpers for external HTTP scrapers (GitHub, Pastebin, etc.).
"""

from __future__ import annotations

import random
import threading
import time
from typing import Optional


class RateLimiter:
    """
    Simple token-bucket-like limiter for GitHub API usage.
    """

    def __init__(
        self,
        *,
        max_requests: int,
        window_seconds: float,
        backoff_base: float,
        max_retries: int,
    ) -> None:
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.backoff_base = backoff_base
        self.max_retries = max_retries

        self._lock = threading.Lock()
        self._window_start = time.time()
        self._count = 0

    def wait_if_needed(self) -> None:
        with self._lock:
            now = time.time()
            if now - self._window_start >= self.window_seconds:
                self._window_start = now
                self._count = 0

            if self._count < self.max_requests:
                self._count += 1
                return

            sleep_for = self.window_seconds - (now - self._window_start)
            if sleep_for > 0:
                time.sleep(sleep_for)
            self._window_start = time.time()
            self._count = 1

    def handle_rate_limit_response(self, _resp) -> Optional[float]:
        """
        Hook for handling 403/429 responses.
        """
        return self.window_seconds

    def backoff(self, attempt: int) -> bool:
        if attempt >= self.max_retries:
            return False
        delay = self.backoff_base * (2**attempt)
        time.sleep(delay)
        return True


class PastebinRateLimiter:
    """
    Very simple per-request delay with jitter for Pastebin scraping.
    """

    def __init__(self, *, min_delay: float, max_delay: float, jitter: float) -> None:
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.jitter = jitter

    def wait(self) -> None:
        base = random.uniform(self.min_delay, self.max_delay)
        jitter = random.uniform(-self.jitter, self.jitter)
        delay = max(0.0, base + jitter)
        time.sleep(delay)


__all__ = ["RateLimiter", "PastebinRateLimiter"]

