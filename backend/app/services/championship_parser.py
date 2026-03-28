"""
Championship name parser - extracts structured fields from championship names.
"""

import re
from typing import Dict, List, Optional, Set


# Known discipline patterns (compound first, then simple)
DISCIPLINE_PATTERNS = [
    r"Place\s*Libre\s*/\s*Chistera\s*Joko\s*Garbi",
    r"Place\s*Libre\s*/\s*Grand\s*Chistera",
    r"Trinquet\s*/\s*Main\s*Nue",
    r"Place\s*Libre",
    r"Main\s*Nue",
    r"Chistera",
    r"Joko\s*Garbi",
    r"Paleta",
    r"Frontenis",
]

ORGANIZATION_KEYWORDS = ["CTPB", "FFPB", "Comité", "Fédération"]

GROUP_KEYWORDS = [
    "GROUPE A", "GROUPE B", "GROUPE C", "GROUPE D",
    "M19", "M17", "M15",
    "Cadets", "Juniors", "Seniors", "Gazteak", "Txikiak",
]

POOL_KEYWORDS = [
    "Poule phase 1", "Poule phase 2", "Poule phase 3",
    "Poule A", "Poule B", "Poule C", "Poule D",
    "Finale", "Demi-finale", "1/2 finale", "1/4 finale",
    "Barrage", "Phase",
]

SERIES_KEYWORDS = [
    "1ère Série", "2ème Série", "3ème Série",
    "1.Maila", "2.Maila", "3.Maila",
    "Série A", "Série B",
]


def parse_championship_name(name: str) -> Dict[str, Optional[str]]:
    """Parse championship name into structured fields."""
    if not name or not isinstance(name, str):
        return {}
    
    result: Dict[str, Optional[str]] = {}
    normalized = name.strip()
    
    # Organization
    for org in ORGANIZATION_KEYWORDS:
        if org.upper() in normalized.upper():
            result["organization"] = org
            break
    
    # Year/Season
    full_season = re.search(r"\b(20\d{2})-(20\d{2})\b", normalized)
    short_season = re.search(r"\b(\d{2})-(\d{2})\b", normalized)
    single_year = re.search(r"\b(20\d{2})\b", normalized)
    
    if full_season:
        result["season"] = f"{full_season.group(1)}-{full_season.group(2)}"
        result["year"] = int(full_season.group(2))
    elif short_season:
        s, e = int(short_season.group(1)), int(short_season.group(2))
        if s > e:
            s, e = 1900 + s, 2000 + e
        else:
            s, e = 2000 + s, 2000 + e
        result["season"] = f"{s}-{e}"
        result["year"] = e
    elif single_year:
        result["season"] = single_year.group(1)
        result["year"] = int(single_year.group(1))
    
    # Discipline (compound first)
    for pattern in DISCIPLINE_PATTERNS:
        match = re.search(pattern, normalized, re.IGNORECASE)
        if match:
            result["discipline"] = match.group(0).strip()
            break
    
    # Pool (exact match, longer patterns first)
    for pool in sorted(POOL_KEYWORDS, key=len, reverse=True):
        if pool in normalized:
            result["pool"] = pool
            break
    
    # Series
    for series in sorted(SERIES_KEYWORDS, key=len, reverse=True):
        if series in normalized:
            result["series"] = series
            break
    
    # Group (word boundary to avoid partial matches)
    for group in sorted(GROUP_KEYWORDS, key=len, reverse=True):
        if re.search(rf"\b{re.escape(group)}\b", normalized, re.IGNORECASE):
            result["group"] = group
            break
    
    return result


def extract_filter_options(championship_names: List[str]) -> Dict[str, List[str]]:
    """Extract distinct filter options from championship names."""
    options: Dict[str, Set[str]] = {
        "disciplines": set(), "seasons": set(), "years": set(),
        "series": set(), "groups": set(), "pools": set(), "organizations": set(),
    }
    
    for name in championship_names:
        parsed = parse_championship_name(name)
        for key in options:
            if parsed.get(key):
                options[key].add(str(parsed[key]))
    
    return {k: sorted(list(v)) for k, v in options.items()}
