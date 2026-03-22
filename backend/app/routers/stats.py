"""Stats endpoints for dashboard analytics."""

from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.dependencies import get_db
from app.services.stats_service import (
    get_summary_stats,
    get_top_players,
    get_top_clubs,
    get_competition_stats,
    get_discipline_stats,
    get_timeline_stats,
)

router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/summary")
async def get_summary(
    db: Session = Depends(get_db),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get overall summary statistics (total games, players, clubs, competitions)."""
    return get_summary_stats(
        db=db,
        competition_id=competition,
        discipline_id=discipline,
        season=season,
        club_id=club,
        player_id=player,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )


@router.get("/players")
async def get_players_stats(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get top players by wins and games count."""
    return {
        "players": get_top_players(
            db=db,
            limit=limit,
            competition_id=competition,
            discipline_id=discipline,
            season=season,
            club_id=club,
            player_id=player,
            date_from=date_from,
            date_to=date_to,
            phase=phase,
        )
    }


@router.get("/clubs")
async def get_clubs_stats(
    db: Session = Depends(get_db),
    limit: int = Query(20, ge=1, le=100, description="Max results"),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get top clubs by games count and wins."""
    return {
        "clubs": get_top_clubs(
            db=db,
            limit=limit,
            competition_id=competition,
            discipline_id=discipline,
            season=season,
            club_id=club,
            player_id=player,
            date_from=date_from,
            date_to=date_to,
            phase=phase,
        )
    }


@router.get("/competitions")
async def get_competitions_stats(
    db: Session = Depends(get_db),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get stats per competition."""
    return {
        "competitions": get_competition_stats(
            db=db,
            competition_id=competition,
            discipline_id=discipline,
            season=season,
            club_id=club,
            player_id=player,
            date_from=date_from,
            date_to=date_to,
            phase=phase,
        )
    }


@router.get("/disciplines")
async def get_disciplines_stats(
    db: Session = Depends(get_db),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get stats per discipline."""
    return {
        "disciplines": get_discipline_stats(
            db=db,
            competition_id=competition,
            discipline_id=discipline,
            season=season,
            club_id=club,
            player_id=player,
            date_from=date_from,
            date_to=date_to,
            phase=phase,
        )
    }


@router.get("/timeline")
async def get_timeline(
    db: Session = Depends(get_db),
    competition: Optional[str] = Query(None, description="Filter by competition ID"),
    discipline: Optional[str] = Query(None, description="Filter by discipline ID"),
    season: Optional[int] = Query(None, description="Filter by season year"),
    club: Optional[str] = Query(None, description="Filter by club ID"),
    player: Optional[str] = Query(None, description="Filter by player ID"),
    date_from: Optional[date] = Query(None, description="Filter from date"),
    date_to: Optional[date] = Query(None, description="Filter to date"),
    phase: Optional[str] = Query(None, description="Filter by phase"),
):
    """Get games over time (monthly)."""
    return {
        "timeline": get_timeline_stats(
            db=db,
            competition_id=competition,
            discipline_id=discipline,
            season=season,
            club_id=club,
            player_id=player,
            date_from=date_from,
            date_to=date_to,
            phase=phase,
        )
    }
