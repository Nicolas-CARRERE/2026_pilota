'''
This file contains the Pydantic models for players, clubs, and teams.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class TeamPlayer(BaseModel):
    """
    Many-to-many link between teams and players.
    Useful for doubles or squad rotations.
    """
    team_id: UUID
    player_id: UUID
    role: Optional[str] = None  # primary, reserve
