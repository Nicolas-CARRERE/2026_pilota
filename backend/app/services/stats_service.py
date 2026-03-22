"""Stats aggregation service for dashboard analytics."""

from datetime import date
from typing import Any, Dict, List, Optional
from sqlalchemy import and_, func, select, or_
from sqlalchemy.orm import Session, joinedload

from app.models.club import Club
from app.models.competition import Competition
from app.models.competition_year import CompetitionYear
from app.models.discipline import Discipline
from app.models.game import Game
from app.models.game_side_player import GameSidePlayer
from app.models.player import Player
from app.models.player_club_history import PlayerClubHistory


def build_game_filters(
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Any]:
    """Build SQLAlchemy filter conditions for games."""
    conditions = []
    
    if competition_id:
        conditions.append(Game.competition_id == competition_id)
    
    if discipline_id:
        conditions.append(Competition.id.in_(
            select(Competition.id).where(Competition.discipline_id == discipline_id)
        ))
    
    if season:
        conditions.append(Competition.id.in_(
            select(Competition.id).join(CompetitionYear).where(CompetitionYear.year == season)
        ))
    
    if club_id:
        conditions.append(
            Game.id.in_(
                select(Game.id)
                .join(GameSidePlayer)
                .join(Player)
                .join(PlayerClubHistory)
                .where(PlayerClubHistory.club_id == club_id)
            )
        )
    
    if player_id:
        conditions.append(
            or_(
                Game.player1_id == player_id,
                Game.player2_id == player_id,
                Game.id.in_(
                    select(GameSidePlayer.game_id).where(
                        GameSidePlayer.player_id == player_id
                    )
                ),
            )
        )
    
    if date_from:
        conditions.append(Game.start_date >= date_from)
    
    if date_to:
        conditions.append(Game.start_date <= date_to)
    
    if phase:
        conditions.append(Game.phase == phase)
    
    return conditions


def get_summary_stats(
    db: Session,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> Dict[str, Any]:
    """Get overall summary statistics."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    games_query = select(Game).where(and_(*filters)) if filters else select(Game)
    games_count = db.execute(select(func.count()).select_from(games_query.subquery())).scalar() or 0
    
    # Get distinct players who participated
    player_ids = set()
    games = db.execute(games_query).scalars().all()
    for game in games:
        player_ids.add(game.player1_id)
        player_ids.add(game.player2_id)
        side_players = db.execute(
            select(GameSidePlayer.player_id).where(GameSidePlayer.game_id == game.id)
        ).scalars().all()
        player_ids.update(side_players)
    
    # Get distinct clubs from player club history
    club_ids = set()
    if player_ids:
        clubs = db.execute(
            select(PlayerClubHistory.club_id).where(
                PlayerClubHistory.player_id.in_(list(player_ids))
            )
        ).scalars().all()
        club_ids.update(clubs)
    
    # Get distinct competitions
    comp_ids = set()
    comps = db.execute(select(Game.competition_id).distinct()).scalars().all()
    comp_ids.update(comps)
    
    # Get distinct disciplines
    disc_ids = set()
    if comp_ids:
        discs = db.execute(
            select(Competition.discipline_id).where(Competition.id.in_(list(comp_ids)))
        ).scalars().all()
        disc_ids.update(discs)
    
    return {
        "total_games": games_count,
        "total_players": len(player_ids),
        "total_clubs": len(club_ids),
        "total_competitions": len(comp_ids),
        "total_disciplines": len(disc_ids),
    }


def get_top_players(
    db: Session,
    limit: int = 20,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get top players by wins and games count."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    games_query = select(Game).where(and_(*filters)) if filters else select(Game)
    games = db.execute(games_query).scalars().all()
    
    # Build player stats map
    player_stats: Dict[str, Dict[str, int]] = {}
    
    for game in games:
        side1_players = [game.player1_id]
        side2_players = [game.player2_id]
        
        side1_players.extend(
            db.execute(
                select(GameSidePlayer.player_id).where(
                    and_(GameSidePlayer.game_id == game.id, GameSidePlayer.side == 1)
                )
            ).scalars().all()
        )
        side2_players.extend(
            db.execute(
                select(GameSidePlayer.player_id).where(
                    and_(GameSidePlayer.game_id == game.id, GameSidePlayer.side == 2)
                )
            ).scalars().all()
        )
        
        # Determine winning side
        winning_side = []
        if game.winner_id:
            if game.winner_id == game.player1_id:
                winning_side = side1_players
            elif game.winner_id == game.player2_id:
                winning_side = side2_players
            else:
                winner_side = db.execute(
                    select(GameSidePlayer.side).where(
                        and_(GameSidePlayer.game_id == game.id, GameSidePlayer.player_id == game.winner_id)
                    )
                ).scalar()
                winning_side = side1_players if winner_side == 1 else side2_players
        
        # Count games and wins for each player
        for pid in side1_players + side2_players:
            if pid not in player_stats:
                player_stats[pid] = {"games": 0, "wins": 0}
            player_stats[pid]["games"] += 1
        
        for pid in winning_side:
            if pid in player_stats:
                player_stats[pid]["wins"] += 1
    
    # Get player details
    player_ids = list(player_stats.keys())
    players = db.execute(
        select(Player).where(Player.id.in_(player_ids))
    ).scalars().all()
    
    result = []
    for player in players:
        stats = player_stats.get(player.id, {"games": 0, "wins": 0})
        result.append({
            "id": player.id,
            "first_name": player.first_name,
            "last_name": player.last_name,
            "nickname": player.nickname,
            "games_played": stats["games"],
            "wins": stats["wins"],
            "losses": stats["games"] - stats["wins"],
        })
    
    # Sort by wins desc, then games desc
    result.sort(key=lambda x: (-x["wins"], -x["games_played"]))
    return result[:limit]


def get_top_clubs(
    db: Session,
    limit: int = 20,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get top clubs by games count and wins."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    games_query = select(Game).where(and_(*filters)) if filters else select(Game)
    games = db.execute(games_query).scalars().all()
    
    # Map club -> stats
    club_stats: Dict[str, Dict[str, int]] = {}
    
    for game in games:
        # Get all players in this game
        player_ids = [game.player1_id, game.player2_id]
        player_ids.extend(
            db.execute(
                select(GameSidePlayer.player_id).where(GameSidePlayer.game_id == game.id)
            ).scalars().all()
        )
        
        # Get clubs for these players
        player_clubs = db.execute(
            select(PlayerClubHistory.player_id, PlayerClubHistory.club_id).where(
                PlayerClubHistory.player_id.in_(player_ids)
            )
        ).all()
        
        # Group by club
        club_players: Dict[str, List[str]] = {}
        for pid, cid in player_clubs:
            if cid:
                if cid not in club_players:
                    club_players[cid] = []
                club_players[cid].append(pid)
        
        # Determine winning side
        winner_ids = []
        if game.winner_id:
            winner_ids.append(game.winner_id)
        
        # Count for each club
        for cid, pids in club_players.items():
            if cid not in club_stats:
                club_stats[cid] = {"games": 0, "wins": 0}
            club_stats[cid]["games"] += 1
            
            # Check if any winner is from this club
            for wid in winner_ids:
                if wid in pids:
                    club_stats[cid]["wins"] += 1
                    break
    
    # Get club details
    club_ids = list(club_stats.keys())
    clubs = db.execute(
        select(Club).where(Club.id.in_(club_ids))
    ).scalars().all()
    
    result = []
    for club in clubs:
        stats = club_stats.get(club.id, {"games": 0, "wins": 0})
        result.append({
            "id": club.id,
            "name": club.name,
            "short_name": club.short_name,
            "games_played": stats["games"],
            "wins": stats["wins"],
        })
    
    result.sort(key=lambda x: (-x["games_played"], -x["wins"]))
    return result[:limit]


def get_competition_stats(
    db: Session,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get stats per competition."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    comp_ids = db.execute(
        select(Game.competition_id).where(and_(*filters)).distinct()
    ).scalars().all() if filters else db.execute(select(Game.competition_id).distinct()).scalars().all()
    
    result = []
    for comp_id in comp_ids:
        comp_filters = filters + [Game.competition_id == comp_id] if filters else [Game.competition_id == comp_id]
        games_count = db.execute(
            select(func.count()).select_from(
                select(Game).where(and_(*comp_filters)).subquery()
            )
        ).scalar() or 0
        
        comp = db.get(Competition, comp_id)
        if comp:
            result.append({
                "competition_id": comp.id,
                "competition_name": comp.id,
                "games_count": games_count,
            })
    
    return result


def get_discipline_stats(
    db: Session,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get stats per discipline."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    comp_ids = db.execute(
        select(Game.competition_id).where(and_(*filters)).distinct()
    ).scalars().all() if filters else db.execute(select(Game.competition_id).distinct()).scalars().all()
    
    disc_stats: Dict[str, int] = {}
    for comp_id in comp_ids:
        comp = db.get(Competition, comp_id)
        if comp:
            did = comp.discipline_id
            disc_stats[did] = disc_stats.get(did, 0) + 1
    
    result = []
    for did, count in disc_stats.items():
        disc = db.get(Discipline, did)
        result.append({
            "discipline_id": did,
            "discipline_name": disc.name if disc else did,
            "games_count": count,
        })
    
    result.sort(key=lambda x: -x["games_count"])
    return result


def get_timeline_stats(
    db: Session,
    competition_id: Optional[str] = None,
    discipline_id: Optional[str] = None,
    season: Optional[int] = None,
    club_id: Optional[str] = None,
    player_id: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    phase: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Get games over time (monthly)."""
    filters = build_game_filters(
        competition_id=competition_id,
        discipline_id=discipline_id,
        season=season,
        club_id=club_id,
        player_id=player_id,
        date_from=date_from,
        date_to=date_to,
        phase=phase,
    )
    
    games_query = select(Game).where(and_(*filters)) if filters else select(Game)
    games = db.execute(games_query).scalars().all()
    
    monthly: Dict[str, int] = {}
    for game in games:
        month_key = game.start_date.strftime("%Y-%m")
        monthly[month_key] = monthly.get(month_key, 0) + 1
    
    result = [{"month": k, "games_count": v} for k, v in sorted(monthly.items())]
    return result
