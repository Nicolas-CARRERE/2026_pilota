"""
CTPB resultats.php HTML parser.

Parses pelote basque results from CTPB (Comité Territorial Pays Basque)
resultats.php pages into structured game rows.
"""

import re
from typing import Any, Dict, List, Optional, Tuple

from bs4 import BeautifulSoup


# -----------------------
# Helper functions
# -----------------------

def _extract_no_renc_from_link(anchor) -> Optional[str]:
    """Extract no_renc from resultats2.php link href."""
    if not anchor or not hasattr(anchor, "get"):
        return None
    href = anchor.get("href") or ""
    match = re.search(r"no_renc=(\d+)", href)
    return match.group(1) if match else None


def _parse_players_from_cell(cell) -> List[Dict[str, str]]:
    """Extract player id (license) and name from club cell li elements.

    Expected formats: "(license) Name", "Name (license)", or plain "license".
    When the visible part is only digits (license), we set name to "" so the
    ingest layer stores the license in license field and uses a placeholder for display.
    """
    players: List[Dict[str, str]] = []
    if not cell:
        return players

    for li in cell.find_all("li"):
        text = li.get_text(strip=True) if li else ""
        if not text:
            continue

        # "(12345) Name" or "(12345) 12345" (license repeated)
        match = re.match(r"\((\d+)\)\s*(.+)", text)
        if match:
            license_id = match.group(1)
            name_part = match.group(2).strip()
            if re.match(r"^\d+$", name_part):
                name_part = ""  # Second part is license again, not a name
            players.append({"license": license_id, "name": name_part})
            continue

        # "Name (12345)"
        match_trailing = re.match(r"(.+?)\s*\((\d+)\)\s*$", text)
        if match_trailing:
            name_part = match_trailing.group(1).strip()
            players.append({"license": match_trailing.group(2), "name": name_part})
            continue

        # Plain digits only: license number only
        if re.match(r"^\d+$", text):
            players.append({"license": text, "name": ""})
            continue

        # Special cases like "(E)" or "(S)"
        if re.match(r"\([A-Z]\)", text):
            players.append({"license": "", "name": text})

    return players

def _parse_club_name_and_players(cell) -> Tuple[str, List[Dict[str, str]]]:
    """Extract club name and players from a club cell."""
    if not cell:
        return "", []
    text_parts: List[str] = []
    for child in cell.children:
        if hasattr(child, "name") and child.name == "span" and "small" in (child.get("class") or []):
            break
        if hasattr(child, "get_text"):
            text_parts.append(child.get_text())
        elif isinstance(child, str):
            text_parts.append(child)
    club_name = "".join(text_parts).replace("\xa0", " ").strip()
    players = _parse_players_from_cell(cell)
    return club_name, players


def _normalize_score(raw: str) -> str:
    """Normalize score string."""
    return (raw or "").replace("\xa0", " ").strip()


def _infer_status(raw_score: str) -> str:
    """Infer game status from raw score."""
    s = (raw_score or "").strip()
    if not s:
        return "unknown"
    if "FG" in s.upper():
        return "forfait"
    if "/P" in s or "P/" in s:
        return "incomplete"
    if re.match(r"^\d+/\d+$", s):
        return "completed"
    return "unknown"


# -----------------------
# Resultats HTML parser
# -----------------------

def parse_resultats_html(html: str) -> List[Dict[str, Any]]:
    """Parse CTPB resultats.php HTML into structured game rows."""
    soup = BeautifulSoup(html, "html.parser")
    games: List[Dict[str, Any]] = []
    current_discipline: str = ""

    table = soup.find("table", class_="mBloc")
    if not table:
        return games

    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if not cells:
            continue

        first_cell = cells[0]
        colspan = first_cell.get("colspan")
        if colspan and int(colspan) >= 7:
            text = first_cell.get_text(strip=True)
            if text:
                text_lower = text.lower()
                if (
                    "Place Libre" in text
                    or "Chistera" in text
                    or "Main Nue" in text
                    or "trinquet" in text_lower
                    or "mur à gauche" in text_lower
                    or "mur a gauche" in text_lower
                    or "paleta" in text_lower
                ):
                    current_discipline = text
            continue

        if first_cell.get("class") and "mTitreSmall" in first_cell.get("class", []):
            continue

        link_cell = first_cell.find("a", href=re.compile(r"resultats2\.php"))
        no_renc = _extract_no_renc_from_link(link_cell) if link_cell else None
        if not no_renc:
            continue

        if len(cells) < 6:
            continue

        date_cell, club1_cell, club2_cell, score_cell = cells[1:5]
        comment_cell = cells[5] if len(cells) > 5 else None

        date_text = date_cell.get_text(strip=True).replace("\xa0", " ")
        club1_name, club1_players = _parse_club_name_and_players(club1_cell)
        club2_name, club2_players = _parse_club_name_and_players(club2_cell)
        raw_score = _normalize_score(score_cell.get_text())
        comment = _normalize_score(comment_cell.get_text()) if comment_cell else ""

        games.append({
            "no_renc": no_renc,
            "date": date_text,
            "club1_name": club1_name,
            "club2_name": club2_name,
            "club1_players": club1_players,
            "club2_players": club2_players,
            "raw_score": raw_score,
            "comment": comment,
            "status": _infer_status(raw_score),
            "discipline_context": current_discipline,
        })

    return games