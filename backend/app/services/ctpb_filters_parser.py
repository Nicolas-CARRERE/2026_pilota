"""
CTPB resultats.php filters HTML parser.

Parses filter form options (competitions, specialties, cities, clubs,
categories, phases, date range) from CTPB resultats.php page HTML.
No router or FastAPI dependency; pure parsing only.
"""

import logging
from typing import Any, Dict, List

from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

SELECT_NAMES = ("InCompet", "InSpec", "InVille", "InClub", "InCat", "InPhase")
OUTPUT_KEYS = (
    "competitions",
    "specialties",
    "cities",
    "clubs",
    "categories",
    "phases",
)


def _options_from_select(select) -> List[Dict[str, str]]:
    """
    Extract {value, label} from a select element, skipping disabled options.

    Args:
        select: BeautifulSoup element for a <select>.

    Returns:
        List of dicts with "value" and "label" keys.
    """
    options: List[Dict[str, str]] = []
    if not select:
        return options
    for opt in select.find_all("option"):
        if opt.get("disabled"):
            continue
        value = (opt.get("value") or "").strip()
        label = (opt.get_text() or "").replace("\xa0", " ").strip()
        options.append({"value": value, "label": label})
    return options


def parse_ctpb_filters_html(html: str) -> Dict[str, Any]:
    """
    Parse CTPB resultats.php HTML and return structured filter options.

    Uses only the form table: selects InCompet, InSpec, InVille, InClub,
    InCat, InPhase (disabled options excluded) and date inputs InDate, InDatef.

    Args:
        html: Raw HTML string from the resultats.php page.

    Returns:
        Dict with keys: competitions, specialties, cities, clubs,
        date_range (start, end), categories, phases, error (None or str).
        Option lists contain {"value": str, "label": str}; disabled options
        are omitted.
    """
    result: Dict[str, Any] = {
        "competitions": [],
        "specialties": [],
        "cities": [],
        "clubs": [],
        "date_range": {"start": "", "end": ""},
        "categories": [],
        "phases": [],
        "error": None,
    }

    try:
        soup = BeautifulSoup(html, "html.parser")

        for select_name, output_key in zip(SELECT_NAMES, OUTPUT_KEYS):
            select = soup.find("select", {"name": select_name})
            result[output_key] = _options_from_select(select)

        start_input = soup.find("input", {"name": "InDate"})
        end_input = soup.find("input", {"name": "InDatef"})
        result["date_range"] = {
            "start": (start_input.get("value") or "").strip() if start_input else "",
            "end": (end_input.get("value") or "").strip() if end_input else "",
        }
    except Exception as e:
        error_msg = f"Error parsing CTPB filters: {e!s}"
        logger.error(error_msg)
        result["error"] = error_msg

    return result
