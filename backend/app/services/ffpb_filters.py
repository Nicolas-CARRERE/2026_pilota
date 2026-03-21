"""FFPB filter options. Returns placeholder or scraped form options."""

from typing import Any, Dict

from app.schemas.ffpb import FFPBFiltersResponse
from app.services.scraper import scrape_logger


async def fetch_ffpb_filters() -> Dict[str, Any]:
    """
    Return FFPB filter options for competitions, categories, disciplines, phases.

    Currently returns a placeholder structure so the Node API can sync to
    ScrapedFilterOption. Replace with real form scraping when FFPB form
    structure is known.
    """
    scrape_logger.info("source=ffpb action=filters step=start")
    data = {
        "years": [{"value": "2026", "label": "2026"}, {"value": "2025", "label": "2025"}],
        "competition_types": [
            {"value": "all", "label": "TOUTES"},
            {"value": "championnat", "label": "CHAMPIONNAT DE FRANCE"},
            {"value": "challenge", "label": "CHALLENGE NATIONAL"},
            {"value": "tournoi", "label": "TOURNOI FEDERAL"},
            {"value": "coupe", "label": "COUPE DE FRANCE"},
        ],
        "categories": [
            {"value": "0", "label": "TOUTES"},
            {"value": "M16", "label": "M16 (moins de 16 ans)"},
            {"value": "M19", "label": "M19 (moins de 19 ans)"},
            {"value": "M22", "label": "M22 (moins de 22 ans)"},
            {"value": "senior", "label": "Sénior"},
        ],
        "disciplines": [
            {"value": "0", "label": "TOUTES"},
            {"value": "cesta_punta_m", "label": "Fronton mur à gauche Cesta Punta Masculin"},
            {"value": "chistera_jg", "label": "Fronton mur à gauche Chistera Joko Garbi"},
            {"value": "paleta_gomme_creuse_f", "label": "Fronton mur à gauche Paleta Pelote de Gomme Creuse Féminine Individuelle"},
        ],
        "locations": [
            {"value": "0", "label": "TOUTES"},
            {"value": "HOSSEGOR", "label": "HOSSEGOR"},
            {"value": "BAYONNE", "label": "BAYONNE"},
            {"value": "ST-PALAIS", "label": "ST-PALAIS"},
        ],
        "phases": [
            {"value": "0", "label": "TOUTES"},
            {"value": "poules", "label": "Poules"},
            {"value": "barrage", "label": "Barrage"},
            {"value": "1/4", "label": "1/4 finale"},
            {"value": "1/2", "label": "1/2 finale"},
            {"value": "finale", "label": "Finale"},
        ],
        "error": None,
    }
    scrape_logger.info(
        "source=ffpb action=filters step=done years=%s competition_types=%s categories=%s disciplines=%s locations=%s phases=%s",
        len(data.get("years", [])),
        len(data.get("competition_types", [])),
        len(data.get("categories", [])),
        len(data.get("disciplines", [])),
        len(data.get("locations", [])),
        len(data.get("phases", [])),
    )
    return data


def to_ffpb_filters_response(data: Dict[str, Any]) -> FFPBFiltersResponse:
    """Convert dict to FFPBFiltersResponse."""
    return FFPBFiltersResponse(
        years=data.get("years", []),
        competition_types=data.get("competition_types", []),
        categories=data.get("categories", []),
        disciplines=data.get("disciplines", []),
        locations=data.get("locations", []),
        phases=data.get("phases", []),
        error=data.get("error"),
    )
