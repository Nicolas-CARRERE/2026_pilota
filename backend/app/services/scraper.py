"""Scraper service: fetches URLs and returns structured payloads."""

import asyncio
import logging
import os
import random
from datetime import datetime, timezone
from typing import Any, List, Optional
from urllib.parse import parse_qs, urlencode, urlparse

import httpx

scrape_logger = logging.getLogger("pelota.scraping")

from app.config import get_settings
from app.schemas.scraping import ScrapeError, ScrapeRunResponse
from app.schemas.scraping import build_resultats_filters_url
from app.services.ctpb_filters_parser import parse_ctpb_filters_html
from app.services.ctpb_parser import parse_resultats_html


async def scrape_url(url: str, timeout_seconds: Optional[float] = None) -> ScrapeRunResponse:
    """
    Scrape a single URL and return structured response.

    Handles: success, partial, failed, timeout, 404, 429 (rate limit).

    Args:
        url: URL to fetch.
        timeout_seconds: Override default timeout.

    Returns:
        ScrapeRunResponse with status, raw_content, and any errors.
    """
    settings = get_settings()
    effective_timeout = timeout_seconds if timeout_seconds is not None else settings.timeout_seconds
    started_at = datetime.now(timezone.utc)
    scrape_logger.info(
        "source=scrape action=run url=%s timeout=%s",
        url[:80] + "..." if len(url) > 80 else url,
        effective_timeout,
    )

    # CTPB resultats.php returns the results table only when submitted via POST.
    if _is_ctpb_resultats_url(url):
        post_body = _ctpb_resultats_post_body_from_url(url)
        if post_body is not None:
            request_headers = {
                "User-Agent": "PelotaScraper/1.0",
                "Content-Type": "application/x-www-form-urlencoded",
                "Origin": "https://ctpb.euskalpilota.fr",
                "Referer": "https://ctpb.euskalpilota.fr/resultats.php",
            }
            async with httpx.AsyncClient(
                timeout=effective_timeout,
                follow_redirects=True,
                headers=request_headers,
            ) as client:
                try:
                    # Establish session so POST returns the results table (site sends form page without mBloc when no cookie).
                    await client.get(CTPB_RESULTATS_BASE_URL)
                    await asyncio.sleep(random.uniform(0.5, 1.5))
                    response = await client.post(
                        CTPB_RESULTATS_BASE_URL,
                        content=post_body,
                    )
                except httpx.TimeoutException as timeout_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=timeout url=%s message=%s",
                        url[:80],
                        timeout_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="timeout", message=str(timeout_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
                except httpx.ConnectError as connect_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=network url=%s message=%s",
                        url[:80],
                        connect_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="network", message=str(connect_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
                except httpx.HTTPError as http_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=network url=%s message=%s",
                        url[:80],
                        http_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="network", message=str(http_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
        else:
            # Fallback to GET if we could not build body (e.g. no query string).
            async with httpx.AsyncClient(
                timeout=effective_timeout,
                follow_redirects=True,
                headers={"User-Agent": "PelotaScraper/1.0"},
            ) as client:
                try:
                    response = await client.get(url)
                except httpx.TimeoutException as timeout_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=timeout url=%s message=%s",
                        url[:80],
                        timeout_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="timeout", message=str(timeout_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
                except httpx.ConnectError as connect_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=network url=%s message=%s",
                        url[:80],
                        connect_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="network", message=str(connect_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
                except httpx.HTTPError as http_exception:
                    scrape_logger.warning(
                        "source=scrape action=run status=failed code=network url=%s message=%s",
                        url[:80],
                        http_exception,
                    )
                    return ScrapeRunResponse(
                        status="failed",
                        errors=[ScrapeError(url=url, code="network", message=str(http_exception))],
                        started_at=started_at,
                        ended_at=datetime.now(timezone.utc),
                    )
    else:
        async with httpx.AsyncClient(
            timeout=effective_timeout,
            follow_redirects=True,
            headers={"User-Agent": "PelotaScraper/1.0"},
        ) as client:
            try:
                response = await client.get(url)
            except httpx.TimeoutException as timeout_exception:
                scrape_logger.warning(
                    "source=scrape action=run status=failed code=timeout url=%s message=%s",
                    url[:80],
                    timeout_exception,
                )
                return ScrapeRunResponse(
                    status="failed",
                    errors=[ScrapeError(url=url, code="timeout", message=str(timeout_exception))],
                    started_at=started_at,
                    ended_at=datetime.now(timezone.utc),
                )
            except httpx.ConnectError as connect_exception:
                scrape_logger.warning(
                    "source=scrape action=run status=failed code=network url=%s message=%s",
                    url[:80],
                    connect_exception,
                )
                return ScrapeRunResponse(
                    status="failed",
                    errors=[ScrapeError(url=url, code="network", message=str(connect_exception))],
                    started_at=started_at,
                    ended_at=datetime.now(timezone.utc),
                )
            except httpx.HTTPError as http_exception:
                scrape_logger.warning(
                    "source=scrape action=run status=failed code=network url=%s message=%s",
                    url[:80],
                    http_exception,
                )
                return ScrapeRunResponse(
                    status="failed",
                    errors=[ScrapeError(url=url, code="network", message=str(http_exception))],
                    started_at=started_at,
                    ended_at=datetime.now(timezone.utc),
                )

    ended_at = datetime.now(timezone.utc)

    if response.status_code == 404:
        scrape_logger.warning(
            "source=scrape action=run status=failed code=not_found url=%s", url[:80]
        )
        return ScrapeRunResponse(
            status="failed",
            errors=[ScrapeError(url=url, code="not_found", message="Resource not found")],
            started_at=started_at,
            ended_at=ended_at,
        )

    if response.status_code == 429:
        scrape_logger.warning(
            "source=scrape action=run status=failed code=rate_limit url=%s", url[:80]
        )
        return ScrapeRunResponse(
            status="failed",
            errors=[ScrapeError(url=url, code="rate_limit", message="Rate limit exceeded")],
            started_at=started_at,
            ended_at=ended_at,
        )

    if response.status_code >= 400:
        scrape_logger.warning(
            "source=scrape action=run status=failed code=http_error url=%s status_code=%s",
            url[:80],
            response.status_code,
        )
        return ScrapeRunResponse(
            status="failed",
            errors=[
                ScrapeError(
                    url=url,
                    code="http_error",
                    message=f"HTTP {response.status_code}: {response.reason_phrase}",
                )
            ],
            started_at=started_at,
            ended_at=ended_at,
        )

    if response.status_code != 200:
        scrape_logger.warning(
            "source=scrape action=run status=failed code=unexpected url=%s status_code=%s",
            url[:80],
            response.status_code,
        )
        return ScrapeRunResponse(
            status="failed",
            errors=[
                ScrapeError(
                    url=url,
                    code="unexpected",
                    message=f"Unexpected status {response.status_code}",
                )
            ],
            started_at=started_at,
            ended_at=ended_at,
        )

    content_type = response.headers.get("content-type", "")
    if content_type.startswith("application/json"):
        try:
            raw_content: dict[str, Any] = response.json()
        except Exception as parse_exception:
            scrape_logger.warning(
                "source=scrape action=run status=failed code=parse url=%s message=%s",
                url[:80],
                parse_exception,
            )
            return ScrapeRunResponse(
                status="failed",
                errors=[ScrapeError(url=url, code="parse", message=f"Invalid JSON: {parse_exception}")],
                started_at=started_at,
                ended_at=ended_at,
            )
    elif _is_ctpb_url(url) and content_type.startswith("text/html"):
        try:
            games = parse_resultats_html(response.text)
            raw_content = {"games": games, "_content_type": content_type}
        except Exception as parse_exception:
            scrape_logger.warning(
                "source=scrape action=run status=failed code=parse url=%s message=CTPB parse error: %s",
                url[:80],
                parse_exception,
            )
            return ScrapeRunResponse(
                status="failed",
                errors=[ScrapeError(url=url, code="parse", message=f"CTPB parse error: {parse_exception}")],
                started_at=started_at,
                ended_at=ended_at,
            )
    else:
        raw_content = {"_raw_text": response.text[:10000], "_content_type": content_type}

    if isinstance(raw_content, dict):
        extracted_items = raw_content.get(
            "games", raw_content.get("items", raw_content.get("data", [raw_content]))
        )
    else:
        extracted_items = [raw_content] if raw_content else []

    total_item_count = len(extracted_items) if isinstance(extracted_items, list) else 1
    items_with_scores_count = _count_items_with_scores(extracted_items)
    duration_sec = (ended_at - started_at).total_seconds()
    scrape_logger.info(
        "source=scrape action=run status=success url=%s duration_sec=%.2f total_items=%s items_with_scores=%s",
        url[:80] if len(url) <= 80 else url[:80] + "...",
        duration_sec,
        total_item_count,
        items_with_scores_count,
    )

    return ScrapeRunResponse(
        status="success",
        raw_content=raw_content if isinstance(raw_content, dict) else {"data": raw_content},
        total_items=total_item_count,
        items_with_scores=items_with_scores_count,
        started_at=started_at,
        ended_at=ended_at,
    )


# Min/max delay (seconds) between first and second request so the server
# returns resultats.php instead of redirecting to the home page.
# Updated for rate limiting (DEV/TEST ONLY - respect robots.txt)
CTPB_FILTERS_DELAY_MIN_SECONDS = float(os.getenv("CTPB_REQUEST_DELAY_MIN_SECONDS", "5.0"))
CTPB_FILTERS_DELAY_MAX_SECONDS = float(os.getenv("CTPB_REQUEST_DELAY_MAX_SECONDS", "10.0"))

# CTPB filters do many GETs with delays; use a longer per-request timeout to avoid
# "Server disconnected" / read timeouts when the site is slow.
CTPB_FILTERS_DEFAULT_TIMEOUT_SECONDS = 120.0

# Rate limiting constants (DEV/TEST ONLY)
CTPB_MAX_COMBINATIONS_PER_RUN = int(os.getenv("CTPB_MAX_COMBINATIONS_PER_RUN", "5"))
CTPB_RATE_LIMIT_PER_MINUTE = int(os.getenv("CTPB_RATE_LIMIT_PER_MINUTE", "10"))


async def fetch_ctpb_filters(
    timeout_seconds: Optional[float] = None,
    competition_value: Optional[str] = None,
    fetch_specialties_per_competition: bool = True,
) -> dict:
    """
    Fetch CTPB resultats.php and parse form filter options.

    Performs two GET requests with a random 1–3 s delay: the first often
    redirects to the home page; only the second response HTML is parsed.

    When competition_value is set, fetches the form for that competition only
    (InSpec options depend on InCompet on CTPB). Returns the same shape with
    specialties for that competition.

    When fetch_specialties_per_competition is True and competition_value is
    not set, after the initial parse fetches the form once per competition
    and fills specialties_by_competition[comp_value] = list of {value, label}.
    The flat "specialties" key remains the first page's list for backward compat.

    Args:
        timeout_seconds: Override default timeout.
        competition_value: If set, fetch filters for this InCompet only.
        fetch_specialties_per_competition: If True and competition_value not set,
            do one extra GET per competition to build specialties_by_competition.

    Returns:
        Dict with keys: competitions, specialties, specialties_by_competition
        (when applicable), cities, clubs, date_range, categories, phases, error.
        Option lists are {value, label}; disabled options are excluded.
    """
    settings = get_settings()
    effective_timeout = (
        timeout_seconds
        if timeout_seconds is not None
        else max(settings.timeout_seconds, CTPB_FILTERS_DEFAULT_TIMEOUT_SECONDS)
    )
    
    # DEV/TEST warning
    if settings.ctpb_dev_mode:
        scrape_logger.warning(
            "⚠️  CTPB scraping is DEV/TEST ONLY - respect robots.txt (Disallow: /). "
            "Rate limit: %s req/min, max %s combinations per run",
            settings.ctpb_rate_limit_per_minute,
            settings.ctpb_max_combinations_per_run,
        )
    
    scrape_logger.info(
        "source=ctpb action=filters step=start competition_value=%s fetch_specialties_per_competition=%s timeout=%s",
        competition_value if competition_value else "full",
        fetch_specialties_per_competition,
        effective_timeout,
    )

    if competition_value is not None:
        url = build_resultats_filters_url(competition_value=competition_value)
        async with httpx.AsyncClient(
            timeout=effective_timeout,
            follow_redirects=True,
            headers={"User-Agent": "PelotaScraper/1.0"},
        ) as client:
            await client.get(url)
            delay = random.uniform(CTPB_FILTERS_DELAY_MIN_SECONDS, CTPB_FILTERS_DELAY_MAX_SECONDS)
            await asyncio.sleep(delay)
            response = await client.get(url)
            response.raise_for_status()
        return parse_ctpb_filters_html(response.text)

    url = build_resultats_filters_url(competition_value="")
    async with httpx.AsyncClient(
        timeout=effective_timeout,
        follow_redirects=True,
        headers={"User-Agent": "PelotaScraper/1.0"},
    ) as client:
        # First GETs can get "Server disconnected without sending a response"; retry once.
        for attempt in (1, 2):
            try:
                await client.get(url)
                delay = random.uniform(CTPB_FILTERS_DELAY_MIN_SECONDS, CTPB_FILTERS_DELAY_MAX_SECONDS)
                await asyncio.sleep(delay)
                response = await client.get(url)
                response.raise_for_status()
                break
            except (httpx.RemoteProtocolError, OSError) as e:
                if attempt == 2:
                    raise
                scrape_logger.warning(
                    "source=ctpb action=filters step=first_get attempt=%s error=%s retrying",
                    attempt,
                    e,
                )
                await asyncio.sleep(2.0)

        result = parse_ctpb_filters_html(response.text)
        if result.get("error") or not fetch_specialties_per_competition:
            return result

        # Step 1: list of competitions from the initial page (exclude "Toutes" value "0")
        competitions = [
            opt
            for opt in result.get("competitions", [])
            if (opt.get("value") or "").strip() and (opt.get("value") or "").strip() != "0"
        ]
        
        # Rate limit: only process first N competitions (DEV/TEST ONLY)
        if len(competitions) > CTPB_MAX_COMBINATIONS_PER_RUN:
            scrape_logger.warning(
                "⚠️  Limiting to %s/%s competitions (DEV/TEST mode - respect robots.txt)",
                CTPB_MAX_COMBINATIONS_PER_RUN,
                len(competitions),
            )
            competitions = competitions[:CTPB_MAX_COMBINATIONS_PER_RUN]
        
        scrape_logger.info(
            "source=ctpb action=filters step=1_done competitions_count=%s",
            len(competitions),
        )

        # Step 2: one request per competition to get specialties (double GET + delay each)
        specialties_by_competition: dict = {}
        for comp in competitions:
            comp_val = comp.get("value") or ""
            comp_label = (comp.get("label") or "")[:50]
            scrape_logger.info(
                "source=ctpb action=filters step=2_comp competition=%s label=%s",
                comp_val,
                comp_label,
            )
            await asyncio.sleep(
                random.uniform(CTPB_FILTERS_DELAY_MIN_SECONDS, CTPB_FILTERS_DELAY_MAX_SECONDS)
            )
            try:
                per_comp_url = build_resultats_filters_url(competition_value=comp_val)
                await client.get(per_comp_url)
                delay = random.uniform(
                    CTPB_FILTERS_DELAY_MIN_SECONDS, CTPB_FILTERS_DELAY_MAX_SECONDS
                )
                await asyncio.sleep(delay)
                resp = await client.get(per_comp_url)
                resp.raise_for_status()
                parsed = parse_ctpb_filters_html(resp.text)
                if not parsed.get("error"):
                    specs = parsed.get("specialties", [])
                    specialties_by_competition[comp_val] = specs
                    scrape_logger.debug(
                        "source=ctpb action=filters step=2_comp_done competition=%s specialties_count=%s",
                        comp_val,
                        len(specs),
                    )
            except Exception as e:
                scrape_logger.warning(
                    "source=ctpb action=filters step=2_comp_failed competition=%s error=%s",
                    comp_val,
                    e,
                )
        result["specialties_by_competition"] = specialties_by_competition
        total_specialties = sum(len(s) for s in specialties_by_competition.values())
        scrape_logger.info(
            "source=ctpb action=filters step=2_done competitions_with_specialties=%s specialties_total=%s",
            len(specialties_by_competition),
            total_specialties,
        )
    return result


def _is_ctpb_url(url: str) -> bool:
    """Return True if URL host is CTPB (ctpb.euskalpilota or euskalpilota)."""
    try:
        host = urlparse(url).netloc.lower()
        return "ctpb.euskalpilota" in host or "euskalpilota" in host
    except Exception:
        return False


def _is_ctpb_resultats_url(url: str) -> bool:
    """Return True if URL is CTPB resultats.php (results page to be fetched via POST)."""
    if not _is_ctpb_url(url):
        return False
    try:
        path = (urlparse(url).path or "").lower()
        return "resultats.php" in path and "resultats2.php" not in path
    except Exception:
        return False


CTPB_RESULTATS_BASE_URL = "https://ctpb.euskalpilota.fr/resultats.php"


def _ctpb_resultats_post_body_from_url(url: str) -> Optional[str]:
    """Build application/x-www-form-urlencoded body from CTPB resultats URL query string."""
    try:
        parsed = urlparse(url)
        if not parsed.query:
            return None
        params = parse_qs(parsed.query, keep_blank_values=True)
        # Flatten: take first value per key so urlencode produces InSel=&InCompet=...
        flat = {k: (v[0] if v else "") for k, v in params.items()}
        return urlencode(flat)
    except Exception:
        return None


def _count_items_with_scores(raw_items: Any) -> int:
    """Count items that contain score-like fields."""
    if not isinstance(raw_items, list):
        return 0
    score_field_names = {"score", "scores", "result", "score1", "score2", "raw_score"}
    items_with_scores_count = 0
    for list_item in raw_items:
        if isinstance(list_item, dict):
            item_field_names = set(field_name.lower() for field_name in list_item.keys())
            if item_field_names & score_field_names:
                items_with_scores_count += 1
    return items_with_scores_count
