'''
This file contains the Pydantic models for games and results.
'''
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel


class GameScore(BaseModel):
    game_id: UUID
    score_details: List[ScoreEntry]  # allows points + set scores
    winner_team_id: Optional[UUID] = None
    winner_player_id: Optional[UUID] = None
