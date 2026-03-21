"""Pydantic schemas for FFPB competition.ffpb.net scraping."""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

FFPB_BASE_URL = "https://competition.ffpb.net/FFPB_COMPETITION"


class FFPBResultatsRequest(BaseModel):
    """Request filters for FFPB competition (POST params I5, I4, I7, etc.)."""

    year: Optional[str] = Field(None, description="Année sportive e.g. 2026")
    competition_type: Optional[str] = Field(None, description="Type compétition")
    category: Optional[str] = Field(None, description="Catégorie d'âge e.g. M16")
    discipline: Optional[str] = Field(None, description="Discipline ID or label")
    location: Optional[str] = Field(None, description="Lieu e.g. HOSSEGOR, BAYONNE")
    phase: Optional[str] = Field(None, description="Phase e.g. Poules, 1/4 finale, Finale")


class FFPBGameRow(BaseModel):
    """Normalized game row from FFPB XML (<LIGNE>)."""

    external_id: Optional[str] = Field(None, description="Source match ID if present")
    date: str = Field(..., description="Date e.g. 15/03/2026 à 14:00")
    location: str = Field(default="", description="Lieu du match")
    team1_name: str = Field(default="", description="Équipe 1")
    team2_name: str = Field(default="", description="Équipe 2")
    team1_player_ids: List[str] = Field(default_factory=list)
    team2_player_ids: List[str] = Field(default_factory=list)
    raw_score: str = Field(default="", description="Score brut e.g. 40/26")
    phase: str = Field(default="", description="Phase e.g. Poules, 1/2 finale")
    directives: str = Field(default="", description="Directives / délégué")
    status: str = Field(default="unknown", description="completed, scheduled, incomplete, unknown")
    raw: Dict[str, Any] = Field(default_factory=dict, description="Raw parsed fields")


class FFPBFiltersResponse(BaseModel):
    """Filter options for FFPB (from form or static)."""

    years: List[Dict[str, str]] = Field(default_factory=list)
    competition_types: List[Dict[str, str]] = Field(default_factory=list)
    categories: List[Dict[str, str]] = Field(default_factory=list)
    disciplines: List[Dict[str, str]] = Field(default_factory=list)
    locations: List[Dict[str, str]] = Field(default_factory=list)
    phases: List[Dict[str, str]] = Field(default_factory=list)
    error: Optional[str] = None
