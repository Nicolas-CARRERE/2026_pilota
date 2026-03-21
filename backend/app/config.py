"""Scraper configuration."""

import os
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True)
class ScraperSettings:
    """Scraper timeout, retries, and base URLs."""

    timeout_seconds: float
    max_retries: int
    retry_backoff_factor: float


@lru_cache
def get_settings() -> ScraperSettings:
    """Return cached scraper settings."""
    return ScraperSettings(
        timeout_seconds=float(os.getenv("PELOTA_SCRAPER_HTTP_TIMEOUT_SECONDS", "30.0")),
        max_retries=int(os.getenv("PELOTA_SCRAPER_MAX_RETRY_ATTEMPTS", "3")),
        retry_backoff_factor=float(os.getenv("PELOTA_SCRAPER_RETRY_BACKOFF_FACTOR", "1.5")),
    )
