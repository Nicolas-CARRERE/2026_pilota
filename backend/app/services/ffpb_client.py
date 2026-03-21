"""FFPB competition.ffpb.net HTTP client. POST with form params, returns XML/HTML."""

from typing import Any, Dict, Optional

import httpx

from app.schemas.ffpb import FFPB_BASE_URL, FFPBResultatsRequest
from app.services.scraper import scrape_logger


async def fetch_ffpb(
    params: Optional[Dict[str, Any]] = None,
    timeout_seconds: float = 30.0,
) -> tuple[str, str]:
    """
    POST to FFPB competition portail and return (body_text, content_type).

    Args:
        params: Form data for POST (e.g. I5, I4, I7 for category, discipline, phase).
        timeout_seconds: Request timeout.

    Returns:
        (response_text, content_type). content_type may be "text/xml" or "text/html".
    """
    payload = params or {}
    scrape_logger.info(
        "source=ffpb action=resultats step=start params_keys=%s timeout=%s",
        list(payload.keys()),
        timeout_seconds,
    )
    headers = {
        "User-Agent": "PelotaScraper/1.0",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "text/html, application/xml, text/xml, */*",
    }
    try:
        async with httpx.AsyncClient(
            timeout=timeout_seconds, follow_redirects=True
        ) as client:
            response = await client.post(
                FFPB_BASE_URL,
                data=payload,
                headers=headers,
            )
            response.raise_for_status()
            content_type = (
                response.headers.get("content-type", "")
                .split(";")[0]
                .strip()
                .lower()
            )
            body_len = len(response.text)
            scrape_logger.info(
                "source=ffpb action=resultats step=done status_code=%s content_type=%s response_len=%s",
                response.status_code,
                content_type,
                body_len,
            )
            return response.text, content_type
    except Exception as e:
        scrape_logger.warning(
            "source=ffpb action=resultats step=failed error=%s",
            e,
        )
        raise


def build_ffpb_params(request: FFPBResultatsRequest) -> Dict[str, str]:
    """
    Build POST form params from FFPBResultatsRequest.

    FFPB uses dynamic param names (I5, I4, I7, etc.). Map known filters to placeholder
    keys; adjust when real form structure is known.
    """
    params: Dict[str, str] = {}
    if request.year:
        params["I1"] = request.year  # placeholder
    if request.competition_type:
        params["I2"] = request.competition_type
    if request.category:
        params["I5"] = request.category
    if request.discipline:
        params["I4"] = request.discipline
    if request.location:
        params["I7"] = request.location
    if request.phase:
        params["I8"] = request.phase
    return params
