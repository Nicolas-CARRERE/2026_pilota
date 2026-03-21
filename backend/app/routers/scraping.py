"""Scraping routes for Node.js API to call."""

from typing import List, Optional

from fastapi import APIRouter

from app.schemas.ffpb import FFPBResultatsRequest
from app.schemas.scraping import (
    CTPBPipelineRequest,
    CTPBPipelineResponse,
    CTPBResultatsRequest,
    ScrapeBatchRequest,
    ScrapeRunRequest,
    ScrapeRunResponse,
    build_resultats_url,
)
from app.services.ctpb_pipeline import run_pipeline
from app.services.ffpb_client import build_ffpb_params, fetch_ffpb
from app.services.ffpb_filters import fetch_ffpb_filters
from app.services.ffpb_parser import parse_ffpb_xml
from app.services.scraper import fetch_ctpb_filters, scrape_logger, scrape_url

router = APIRouter()


@router.post("/run", response_model=ScrapeRunResponse)
async def scrape_run(request: ScrapeRunRequest) -> ScrapeRunResponse:
    """
    Trigger scrape for a single source URL.

    Returns scraped payload or structured error.
    """
    scrape_logger.info(
        "source=route route=run url=%s",
        str(request.url)[:80] + "..." if len(str(request.url)) > 80 else str(request.url),
    )
    result = await scrape_url(
        url=str(request.url),
        timeout_seconds=request.timeout_seconds,
    )
    return result


@router.post("/batch")
async def scrape_batch(request: ScrapeBatchRequest):
    """
    Batch scrape multiple sources.

    Returns list of ScrapeRunResponse, one per URL.
    """
    scrape_logger.info(
        "source=route route=batch urls_count=%s",
        len(request.urls),
    )
    scrape_results: List[ScrapeRunResponse] = []
    for url_item in request.urls:
        scrape_result = await scrape_url(url=str(url_item.url))
        scrape_results.append(scrape_result)
    return scrape_results


@router.get("/ctpb/filters")
async def ctpb_filters(
    competition: Optional[str] = None,
    specialties_per_competition: bool = True,
) -> dict:
    """
    Fetch CTPB resultats.php form and return available filter options.

    Query params:
        competition: If set, fetch form for this InCompet only (returns
            specialties for that competition; InSpec options depend on InCompet).
        specialties_per_competition: If True (default) and competition not set,
            fetches the form once per competition and returns
            specialties_by_competition[comp_value] = list of {value, label}.

    Use these values in POST /ctpb/resultats (competition, specialty, ville, club, category, phase).
    """
    scrape_logger.info(
        "source=route route=ctpb_filters competition=%s specialties_per_competition=%s",
        competition or "(full)",
        specialties_per_competition,
    )
    data = await fetch_ctpb_filters(
        competition_value=competition,
        fetch_specialties_per_competition=specialties_per_competition,
    )
    if not data.get("error"):
        scrape_logger.info(
            "source=route route=ctpb_filters done competitions=%s has_specialties_by_competition=%s",
            len(data.get("competitions", [])),
            "specialties_by_competition" in data and bool(data.get("specialties_by_competition")),
        )
    return data


@router.post("/ctpb/resultats")
async def ctpb_resultats(request: CTPBResultatsRequest) -> dict:
    """
    Fetch and parse CTPB resultats.php with optional filters.

    Returns games list and filters_applied.
    """
    url = build_resultats_url(request)
    scrape_logger.info(
        "source=route route=ctpb_resultats competition=%s specialty=%s",
        getattr(request, "competition", None) or "",
        getattr(request, "specialty", None) or "",
    )
    result = await scrape_url(url)
    if result.status != "success" or not result.raw_content:
        return {
            "games": [],
            "filters_applied": request.model_dump(exclude_none=True),
            "error": result.errors[0].message if result.errors else "Scrape failed",
        }
    games = result.raw_content.get("games", [])
    games_count = len(games) if isinstance(games, list) else 0
    scrape_logger.info(
        "source=route route=ctpb_resultats done games_count=%s",
        games_count,
    )
    return {
        "games": games,
        "filters_applied": request.model_dump(exclude_none=True),
    }


@router.post("/ctpb/pipeline", response_model=CTPBPipelineResponse)
async def ctpb_pipeline(request: CTPBPipelineRequest) -> CTPBPipelineResponse:
    """
    Run the full CTPB scraping pipeline.

    Fetches live filter options, generates all (competition × specialty) combinations
    not present in ``already_scraped_urls``, scrapes each one sequentially, and
    returns structured results. The Node.js layer is responsible for supplying
    already-scraped URLs for deduplication and persisting new results.

    Args:
        request: CTPBPipelineRequest with ``already_scraped_urls`` list and optional
            ``max_combinations`` cap.

    Returns:
        CTPBPipelineResponse with per-combination results and aggregate counts.
    """
    scrape_logger.info(
        "source=route route=ctpb_pipeline already_scraped_urls=%s max_combinations=%s competition=%s category=%s",
        len(request.already_scraped_urls),
        request.max_combinations,
        request.competition,
        request.category,
    )
    result = await run_pipeline(
        already_scraped_urls=request.already_scraped_urls,
        max_combinations=request.max_combinations,
        request_delay_seconds=request.request_delay_seconds,
        filter_competition=request.competition,
        filter_category=request.category,
        filter_specialty=request.specialty,
        filter_phase=request.phase,
        filter_ville=request.ville,
        filter_club=request.club,
        filter_date_from=request.date_from,
        filter_date_to=request.date_to,
    )
    scrape_logger.info(
        "source=route route=ctpb_pipeline done combinations_scraped=%s combinations_total=%s",
        result.get("combinations_scraped", 0),
        result.get("combinations_total", 0),
    )
    return CTPBPipelineResponse(**result)


@router.get("/health")
async def scrape_health() -> dict:
    """Health check for Node.js to verify scraper is up."""
    return {"status": "ok", "service": "pelota-scraper"}


# --- FFPB (competition.ffpb.net) ---


@router.get("/ffpb/filters")
async def ffpb_filters() -> dict:
    """
    Return FFPB filter options (year, category, discipline, location, phase).

    Used by Node API to sync to ScrapedFilterOption.
    """
    scrape_logger.info("source=route route=ffpb_filters")
    return await fetch_ffpb_filters()


@router.post("/ffpb/resultats")
async def ffpb_resultats(request: FFPBResultatsRequest) -> dict:
    """
    POST to FFPB competition portail with filters and parse XML response.

    Returns games list (from <WAJAX><CHAMP><LIGNE>...) and filters_applied.
    """
    params = build_ffpb_params(request)
    scrape_logger.info(
        "source=route route=ffpb_resultats params_keys=%s",
        list(params.keys()),
    )
    try:
        text, content_type = await fetch_ffpb(params=params)
    except Exception as e:
        return {
            "games": [],
            "filters_applied": request.model_dump(exclude_none=True),
            "error": str(e),
        }
    if "xml" in content_type or "<WAJAX" in text or "<CHAMP" in text or "<LIGNE" in text:
        games = parse_ffpb_xml(text)
    else:
        games = []
    games_count = len(games) if isinstance(games, list) else 0
    scrape_logger.info(
        "source=route route=ffpb_resultats done games_count=%s",
        games_count,
    )
    return {
        "games": [g for g in games],
        "filters_applied": request.model_dump(exclude_none=True),
    }
