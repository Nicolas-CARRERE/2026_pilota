"""
Championship name parser - extracts structured fields from championship names.

Parses championship names like:
- "Trinquet/Main Nue - Groupe A1ère Série - 1.MailaGROUPE A Poule phase 1"
- "Championnat de France 2026 - Main Nue - 1ère Série - GROUPE A - Poule phase 1"
- "CTPB 2025 - Trinquet - Cadets - Finale"
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

# Known group/age category keywords (order matters - check longer patterns first)
GROUP_KEYWORDS = [
    "GROUPE A",
    "GROUPE B", 
    "GROUPE C",
    "GROUPE D",
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
    "Poule phase 1",
    "Poule phase 2",
    "Poule A",
    "Poule B",
    "Poule C",
    "Poule D",
    "Poule",
    "Finale",
    "Demi-finale",
    "1/2 finale",
    "1/4 finale",
    "Barrage",
    "Phase",
]

# Known series keywords
SERIES_KEYWORDS = [
    "1ère Série",
    "2ème Série",
    "3ème Série",
    "1.Maila",
    "2.Maila",
    "3.Maila",
    "Série A",
    "Série B",
]


def parse_championship_name(name: str) -> Dict[str, Optional[str]]:
    """
    Parse championship name into structured fields.
    
    Handles both delimited (" - ") and concatenated formats.
    
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
    full_season_match = re.search(r"\b(20\d{2})-(20\d{2})\b", normalized)
    short_season_match = re.search(r"\b(\d{2})-(\d{2})\b", normalized)
    single_year_match = re.search(r"\b(20\d{2})\b", normalized)
    
    if full_season_match:
        start_year = int(full_season_match.group(1))
        end_year = int(full_season_match.group(2))
        result["season"] = f"{start_year}-{end_year}"
        result["year"] = end_year
    elif short_season_match:
        start_year = int(short_season_match.group(1))
        end_year = int(short_season_match.group(2))
        if start_year > end_year:
            start_year = 1900 + start_year
            end_year = 2000 + end_year
        else:
            start_year = 2000 + start_year
            end_year = 2000 + end_year
        result["season"] = f"{start_year}-{end_year}"
        result["year"] = end_year
    elif single_year_match:
        year = int(single_year_match.group(1))
        result["season"] = str(year)
        result["year"] = year
    
    # Extract discipline (can be compound like "Trinquet/Main Nue" or "Place Libre/Chistera Joko Garbi")
    for discipline in DISCIPLINE_KEYWORDS:
        # Check if discipline is in the name (with or without slash)
        if re.search(rf"\b{re.escape(discipline)}\b", normalized, re.IGNORECASE):
            # Try to get compound discipline (e.g., "Trinquet/Main Nue")
            compound_match = re.search(
                rf"((?:Place Libre|Trinquet|Main Nue|Chistera|Joko Garbi)(?:\s*/\s*(?:Place Libre|Trinquet|Main Nue|Chistera|Joko Garbi))?)",
                normalized,
                re.IGNORECASE
            )
            if compound_match:
                result["discipline"] = compound_match.group(1).strip()
            else:
                result["discipline"] = discipline
            break
    
    # Extract pool/phase (look for these patterns anywhere in the string)
    for pool in sorted(POOL_KEYWORDS, key=len, reverse=True):
        pool_match = re.search(rf"{re.escape(pool)}", normalized, re.IGNORECASE)
        if pool_match:
            # Extract the pool phrase (may include additional text like "Poule phase 1")
            start = pool_match.start()
            # Try to get the full pool phrase
            remaining = normalized[start:]
            pool_phrase_match = re.match(r"([A-Za-z\s/]+(?:phase\s*\d+)?)", remaining, re.IGNORECASE)
            if pool_phrase_match:
                result["pool"] = pool_phrase_match.group(1).strip()
            else:
                result["pool"] = pool
            break
    
    # Extract series (look for patterns like "1ère Série", "1.Maila", etc.)
    for series in sorted(SERIES_KEYWORDS, key=len, reverse=True):
        series_match = re.search(rf"{re.escape(series)}", normalized, re.IGNORECASE)
        if series_match:
            result["series"] = series
            break
    
    # Extract group (GROUPE A, M19, Cadets, etc.)
    for group in sorted(GROUP_KEYWORDS, key=len, reverse=True):
        group_match = re.search(rf"\b{re.escape(group)}\b", normalized, re.IGNORECASE)
        if group_match:
            result["group"] = group
            break
    
    return result


def extract_filter_options(championship_names: List[str]) -> Dict[str, List[str]]:
    """
    Extract distinct filter options from a list of championship names.
    
    Args:
        championship_names: List of championship name strings
        
    Returns:
        Dict with keys: disciplines, seasons, years, series, groups, pools, organizations
    """
    options: Dict[str, Set[str]] = {
        "disciplines": set(),
        "seasons": set(),
        "years": set(),
        "series": set(),
        "groups": set(),
        "pools": set(),
        "organizations": set(),
    }
    
    for name in championship_names:
        parsed = parse_championship_name(name)
        if parsed.get("discipline"):
            options["disciplines"].add(parsed["discipline"])
        if parsed.get("season"):
            options["seasons"].add(parsed["season"])
        if parsed.get("year"):
            options["years"].add(str(parsed["year"]))
        if parsed.get("series"):
            options["series"].add(parsed["series"])
        if parsed.get("group"):
            options["groups"].add(parsed["group"])
        if parsed.get("pool"):
            options["pools"].add(parsed["pool"])
        if parsed.get("organization"):
            options["organizations"].add(parsed["organization"])
    
    # Convert sets to sorted lists
    return {
        key: sorted(list(value))
        for key, value in options.items()
    }
