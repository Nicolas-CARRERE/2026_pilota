"""
Championship name parser - extracts structured fields from championship names.

Parses championship names like:
- "Championnat de France 2026 - Main Nue - 1ère Série - GROUPE A - Poule phase 1"
- "CTPB 2025 - Trinquet - Cadets - Finale"
- "FFPB Place Libre 2026 - M19 - 1.Maila"
"""

import re
from typing import Dict, List, Optional, Set


# Known discipline keywords (case-insensitive matching)
DISCIPLINE_KEYWORDS = [
    "Place Libre",
    "Trinquet",
    "Main Nue",
    "Chistera",
    "Joko Garbi",
    "Paleta",
    "Gros Paleta",
    "Pala Corta",
    "Xare",
    "Frontenis",
]

# Known organization keywords
ORGANIZATION_KEYWORDS = ["CTPB", "FFPB", "Comité", "Fédération"]

# Known group/age category keywords
GROUP_KEYWORDS = [
    "GROUPE A",
    "GROUPE B",
    "GROUPE C",
    "M19",
    "M17",
    "M15",
    "Cadets",
    "Juniors",
    "Seniors",
    "Gazteak",
    "Txikiak",
]

# Known pool/phase keywords
POOL_KEYWORDS = [
    "Poule",
    "Finale",
    "Demi-finale",
    "1/2 finale",
    "1/4 finale",
    "Barrage",
    "Phase",
]


def parse_championship_name(name: str) -> Dict[str, Optional[str]]:
    """
    Parse championship name into structured fields.

    Args:
        name: Championship name string

    Returns:
        Dict with keys: discipline, season, year, series, group, pool, organization
    """
    if not name or not isinstance(name, str):
        return {}

    result: Dict[str, Optional[str]] = {}
    normalized = name.strip()

    # Extract organization (usually at the beginning)
    for org in ORGANIZATION_KEYWORDS:
        if org.upper() in normalized.upper():
            result["organization"] = org
            break

    # Extract year/season - detect season spans like "2025-2026" or "25-26"
    # Priority: full span (2025-2026) > short span (25-26) > single year (2026)
    full_season_match = re.search(r"\b(20\d{2})-(20\d{2})\b", normalized)
    short_season_match = re.search(r"\b(\d{2})-(\d{2})\b", normalized)
    single_year_match = re.search(r"\b(20\d{2})\b", normalized)

    if full_season_match:
        # Full season span: "2025-2026"
        start_year = int(full_season_match.group(1))
        end_year = int(full_season_match.group(2))
        result["season"] = f"{start_year}-{end_year}"
        result["year"] = str(end_year)
    elif short_season_match:
        # Short season span: "25-26" → "2025-2026"
        start_year = int(short_season_match.group(1))
        end_year = int(short_season_match.group(2))
        # Handle century rollover (e.g., 99-00 → 1999-2000)
        if start_year > end_year:
            start_year = 1900 + start_year
            end_year = 2000 + end_year
        else:
            start_year = 2000 + start_year
            end_year = 2000 + end_year
        result["season"] = f"{start_year}-{end_year}"
        result["year"] = str(end_year)
    elif single_year_match:
        # Single year: "2026" → season: "2026", year: 2026
        year = int(single_year_match.group(1))
        result["year"] = str(year)
        result["season"] = str(year)

    # Extract discipline
    for discipline in DISCIPLINE_KEYWORDS:
        if discipline.upper() in normalized.upper():
            result["discipline"] = discipline
            break

    # Extract series (e.g., "1ère Série", "1.Maila")
    series_match = re.search(r"(\d+(?:ère|ème|º|\.Maila)?\s*(?:Série|Maila)?)", normalized, re.IGNORECASE)
    if series_match:
        result["series"] = series_match.group(1).strip()

    # Extract group/age category
    for group in GROUP_KEYWORDS:
        if group.upper() in normalized.upper():
            result["group"] = group
            break

    # Extract pool/phase
    for pool in POOL_KEYWORDS:
        if pool.upper() in normalized.upper():
            # Try to get more context (e.g., "Poule phase 1" instead of just "Poule")
            pool_regex = re.compile(f"({pool}(?:\\s+(?:phase\\s*\\d+|\\d+))?)", re.IGNORECASE)
            pool_match = pool_regex.search(normalized)
            if pool_match:
                result["pool"] = pool_match.group(1).strip()
            else:
                result["pool"] = pool
            break

    return result


def extract_filter_options(names: List[str]) -> Dict[str, List]:
    """
    Parse multiple championship names and return distinct filter options.

    Args:
        names: List of championship names

    Returns:
        Dict with arrays of distinct values for each field
    """
    disciplines: Set[str] = set()
    seasons: Set[str] = set()
    years: Set[str] = set()
    series: Set[str] = set()
    groups: Set[str] = set()
    pools: Set[str] = set()
    organizations: Set[str] = set()

    for name in names:
        parsed = parse_championship_name(name)
        if parsed.get("discipline"):
            disciplines.add(parsed["discipline"])
        if parsed.get("season"):
            seasons.add(parsed["season"])
        if parsed.get("year"):
            years.add(parsed["year"])
        if parsed.get("series"):
            series.add(parsed["series"])
        if parsed.get("group"):
            groups.add(parsed["group"])
        if parsed.get("pool"):
            pools.add(parsed["pool"])
        if parsed.get("organization"):
            organizations.add(parsed["organization"])

    return {
        "disciplines": sorted(list(disciplines)),
        "seasons": sorted(list(seasons)),
        "years": sorted(list(years), reverse=True),
        "series": sorted(list(series)),
        "groups": sorted(list(groups)),
        "pools": sorted(list(pools)),
        "organizations": sorted(list(organizations)),
    }
