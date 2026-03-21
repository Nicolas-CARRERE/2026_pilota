'''
This file contains the Pydantic models for games and results.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel


class PlayerStat(BaseModel):
    id: UUID
    player_id: UUID
    game_id: UUID
    points_scored: Optional[int] = None
    points_conceded: Optional[int] = None
    # extra stats only if scraped
    aces: Optional[int] = None
    fault_count: Optional[int] = None
