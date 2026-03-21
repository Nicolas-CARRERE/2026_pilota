"""CTPB pipeline service: combination generation and batch scraping orchestration.

Generates all (competition × specialty) URL combinations from live CTPB filter data,
filters out already-scraped combinations, and runs sequential scraping to avoid
rate-limiting the CTPB site.
"""

import asyncio
from typing import Any, Dict, List, Optional, Set

from app.schemas.scraping import (
    CTPBPipelineCombinationResult,
    CTPBResultatsRequest,
    build_resultats_url,
)
from app.services.scraper import fetch_ctpb_filters, scrape_logger, scrape_url


def _phase_value_to_label(phases: List[Dict[str, Any]], value: Optional[str]) -> Optional[str]:
    """Resolve phase filter value to display label from CTPB phases options."""
    if not value:
        return None
    for opt in phases:
        if opt.get("value") == value:
            label = opt.get("label") or value
            return label.strip() if label else None
    return None


def generate_combinations(
    filters: Dict[str, Any],
    already_scraped_urls: Set[str],
    max_combinations: Optional[int] = None,
    filter_competition: Optional[str] = None,
    filter_specialty: Optional[str] = None,
    filter_category: Optional[str] = None,
    filter_phase: Optional[str] = None,
    filter_ville: Optional[str] = None,
    filter_club: Optional[str] = None,
    filter_date_from: Optional[str] = None,
    filter_date_to: Optional[str] = None,
) -> List[CTPBResultatsRequest]:
    """Generate pending (competition × specialty) combinations not yet scraped.

    Uses specialties_by_competition when present (specialties depend on competition
    on CTPB). Otherwise falls back to Cartesian product of competitions × flat
    specialties. When filter_competition or filter_specialty are set, only those
    values are used. filter_category, filter_phase, etc. are applied to every
    generated CTPBResultatsRequest (fixed URL params).

    Args:
        filters: Dict from ``fetch_ctpb_filters()``.
        already_scraped_urls: Set of canonical URLs already successfully scraped.
        max_combinations: Optional hard cap on pending combinations to return.
        filter_competition: If set, only this competition value.
        filter_specialty: If set, only this specialty value per competition.
        filter_category, filter_phase, filter_ville, filter_club, filter_date_*:
            Applied to every combo (fixed params on each URL).

    Returns:
        Ordered list of ``CTPBResultatsRequest`` instances ready to scrape.
    """
    all_competitions = [
        opt for opt in filters.get("competitions", []) if opt.get("value")
    ]
    if filter_competition:
        competitions = [
            c for c in all_competitions if (c.get("value") or "") == filter_competition
        ]
    else:
        competitions = all_competitions

    specialties_by_comp = filters.get("specialties_by_competition") or {}
    flat_specialties = [
        opt
        for opt in filters.get("specialties", [])
        if opt.get("value") not in ("", "0")
    ]

    pending: List[CTPBResultatsRequest] = []

    for competition in competitions:
        comp_val = competition.get("value") or ""
        specialties = specialties_by_comp.get(comp_val)
        if specialties is None:
            specialties = flat_specialties
        else:
            specialties = [
                s for s in specialties if s.get("value") not in ("", "0")
            ]
        if filter_specialty:
            specialties = [s for s in specialties if (s.get("value") or "") == filter_specialty]
        for specialty in specialties:
            combo = CTPBResultatsRequest(
                competition=comp_val,
                specialty=specialty.get("value", ""),
                category=filter_category,
                phase=filter_phase,
                ville=filter_ville,
                club=filter_club,
                date_from=filter_date_from,
                date_to=filter_date_to,
            )
            url = build_resultats_url(combo)
            if url in already_scraped_urls:
                continue
            pending.append(combo)
            if max_combinations is not None and len(pending) >= max_combinations:
                return pending

    return pending


async def run_pipeline(
    already_scraped_urls: List[str],
    max_combinations: Optional[int] = None,
    request_delay_seconds: float = 1.5,
    filter_competition: Optional[str] = None,
    filter_category: Optional[str] = None,
    filter_specialty: Optional[str] = None,
    filter_phase: Optional[str] = None,
    filter_ville: Optional[str] = None,
    filter_club: Optional[str] = None,
    filter_date_from: Optional[str] = None,
    filter_date_to: Optional[str] = None,
) -> Dict[str, Any]:
    """Fetch filters, generate pending combinations, scrape each one sequentially.

    This is the top-level orchestration function called by the FastAPI endpoint.
    Sequential scraping is intentional to avoid rate-limiting the CTPB site.
    Optional filter_* args restrict which combinations are generated and/or fix
    URL params (e.g. InCat, InPhase) on every request.

    Args:
        already_scraped_urls: URLs already successfully scraped.
        max_combinations: Optional cap on combinations to process per run.
        request_delay_seconds: Seconds to sleep between each HTTP request.
        filter_competition: If set, only this competition (InCompet).
        filter_specialty: If set, only this specialty (InSpec) per competition.
        filter_category, filter_phase, filter_ville, filter_club, filter_date_*:
            Applied to every generated URL.

    Returns:
        Dict with keys: filters_fetched, combinations_total, combinations_pending,
        combinations_scraped, results.
    """
    scraped_url_set: Set[str] = set(already_scraped_urls)
    scrape_logger.info(
        "source=ctpb action=pipeline step=start already_scraped_urls=%s max_combinations=%s competition=%s category=%s",
        len(already_scraped_urls),
        max_combinations,
        filter_competition,
        filter_category,
    )

    # When filtering by one competition, fetch only that competition's page (faster).
    if filter_competition:
        filters = await fetch_ctpb_filters(
            competition_value=filter_competition,
            fetch_specialties_per_competition=False,
        )
        # Single-page fetch returns specialties for that competition; ensure shape for generate_combinations.
        if not filters.get("specialties_by_competition"):
            filters["specialties_by_competition"] = {
                filter_competition: filters.get("specialties", []),
            }
        # Restrict competitions list to this one so generate_combinations sees only it.
        all_comp_opts = [
            c for c in filters.get("competitions", []) if (c.get("value") or "") == filter_competition
        ]
        if not all_comp_opts:
            all_comp_opts = [{"value": filter_competition, "label": ""}]
        filters["competitions"] = all_comp_opts
    else:
        filters = await fetch_ctpb_filters()

    await asyncio.sleep(request_delay_seconds)

    all_competitions = [
        opt for opt in filters.get("competitions", []) if opt.get("value")
    ]
    specialties_by_comp = filters.get("specialties_by_competition") or {}
    if specialties_by_comp:
        combinations_total = sum(
            len([s for s in specs if (s.get("value") or "") not in ("", "0")])
            for specs in specialties_by_comp.values()
        )
    else:
        all_specialties = [
            opt
            for opt in filters.get("specialties", [])
            if opt.get("value") not in ("", "0")
        ]
        combinations_total = len(all_competitions) * len(all_specialties)

    pending = generate_combinations(
        filters,
        scraped_url_set,
        max_combinations,
        filter_competition=filter_competition,
        filter_specialty=filter_specialty,
        filter_category=filter_category,
        filter_phase=filter_phase,
        filter_ville=filter_ville,
        filter_club=filter_club,
        filter_date_from=filter_date_from,
        filter_date_to=filter_date_to,
    )
    combinations_pending = len(pending)
    combinations_scraped = 0
    scrape_logger.info(
        "source=ctpb action=pipeline step=filters_done combinations_total=%s combinations_pending=%s",
        combinations_total,
        combinations_pending,
    )

    results: List[CTPBPipelineCombinationResult] = []

    for combo in pending:
        url = build_resultats_url(combo)
        scrape_result = await scrape_url(url)
        scrape_logger.debug(
            "source=ctpb action=pipeline combo url=%s status=%s",
            url[:80] + "..." if len(url) > 80 else url,
            scrape_result.status,
        )

        games_count = 0
        if scrape_result.status == "success" and scrape_result.raw_content:
            games = scrape_result.raw_content.get("games", [])
            games_count = len(games) if isinstance(games, list) else 0
            # Enrich each game with phase label from combo (resolve value -> label via filters)
            phase_label = _phase_value_to_label(filters.get("phases") or [], combo.phase)
            if isinstance(games, list):
                for g in games:
                    if isinstance(g, dict):
                        g["phase"] = phase_label or ""
            combinations_scraped += 1

        results.append(
            CTPBPipelineCombinationResult(
                url=url,
                competition=combo.competition or "",
                specialty=combo.specialty or "",
                status=scrape_result.status,
                games_count=games_count,
                raw_content=scrape_result.raw_content,
                errors=scrape_result.errors,
            )
        )
        await asyncio.sleep(request_delay_seconds)

    scrape_logger.info(
        "source=ctpb action=pipeline step=done combinations_scraped=%s combinations_total=%s",
        combinations_scraped,
        combinations_total,
    )
    return {
        "filters_fetched": True,
        "combinations_total": combinations_total,
        "combinations_pending": combinations_pending,
        "combinations_scraped": combinations_scraped,
        "results": results,
    }
