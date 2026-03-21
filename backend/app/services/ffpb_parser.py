"""FFPB XML response parser. Structure: <WAJAX><CHAMP>...</CHAMP></WAJAX>, <LIGNE> per match."""

import re
import xml.etree.ElementTree as ET
from typing import Any, Dict, List


def _normalize_score(raw: str) -> str:
    """Normalize score string."""
    return (raw or "").strip()


def _infer_status(raw_score: str) -> str:
    """Infer game status from raw score (FFPB style)."""
    s = (raw_score or "").strip()
    if not s:
        return "scheduled"
    if re.match(r"^\d+/\d+", s) or " - " in s:
        return "completed"
    return "unknown"


def parse_ffpb_xml(xml_text: str) -> List[Dict[str, Any]]:
    """
    Parse FFPB XML response into list of game dicts.

    Expects structure <WAJAX><CHAMP>...</CHAMP></WAJAX> with <LIGNE> elements
    or similar. Extracts date, location, teams, score, phase, directives.
    If the XML structure differs, returns empty list or partial data.

    Args:
        xml_text: Raw XML string from FFPB POST response.

    Returns:
        List of dicts with keys: date, location, team1_name, team2_name,
        raw_score, phase, directives, status, team1_player_ids, team2_player_ids, raw.
    """
    games: List[Dict[str, Any]] = []
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return games

    # Handle WAJAX > CHAMP > LIGNE or direct CHAMP > LIGNE
    champ = root.find(".//CHAMP") or root.find("CHAMP") or root
    if champ is None:
        champ = root

    for ligne in champ.findall(".//LIGNE") or champ.findall("LIGNE") or []:
        raw: Dict[str, Any] = {}
        text = (ligne.text or "").strip()
        for child in ligne:
            raw[child.tag] = (child.text or "").strip()
            raw[child.tag + "_tail"] = (child.tail or "").strip()

        # Map common tag names to our model (adjust when real XML sample is available)
        date = raw.get("DATE") or raw.get("date") or raw.get("Date") or ""
        location = raw.get("LIEU") or raw.get("lieu") or raw.get("Lieu") or raw.get("LOCATION") or ""
        team1 = raw.get("EQUIPE1") or raw.get("equipe1") or raw.get("TEAM1") or raw.get("team1") or ""
        team2 = raw.get("EQUIPE2") or raw.get("equipe2") or raw.get("TEAM2") or raw.get("team2") or ""
        score = _normalize_score(raw.get("SCORE") or raw.get("score") or raw.get("Score") or "")
        phase = raw.get("PHASE") or raw.get("phase") or raw.get("Phase") or ""
        directives = raw.get("DIRECTIVES") or raw.get("directives") or raw.get("INFO") or ""

        # If LIGNE has no known children, try parsing inline text
        if not date and not team1 and text:
            raw["_text"] = text

        games.append({
            "external_id": raw.get("ID") or raw.get("id") or None,
            "date": date,
            "location": location,
            "team1_name": team1,
            "team2_name": team2,
            "team1_player_ids": _extract_player_ids(raw.get("TEAM1_IDS") or raw.get("team1_player_ids") or ""),
            "team2_player_ids": _extract_player_ids(raw.get("TEAM2_IDS") or raw.get("team2_player_ids") or ""),
            "raw_score": score,
            "phase": phase,
            "directives": directives,
            "status": _infer_status(score),
            "raw": raw,
        })
    return games


def _extract_player_ids(s: str) -> List[str]:
    """Extract player IDs from a string (e.g. comma-separated or space-separated)."""
    if not s or not isinstance(s, str):
        return []
    ids = re.findall(r"\d{5,}", s)
    return list(dict.fromkeys(ids))
