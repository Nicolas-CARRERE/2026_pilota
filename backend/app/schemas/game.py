'''
This file contains the Pydantic models for games and results.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enums import GameStatusEnum
import datetime

class Game(BaseModel):
    id: UUID
    competition_id: UUID
    round: Optional[str] = None
    game_number: Optional[int] = None
    # team1 vs team2 OR player1 vs player2 (if singles)
    team1_id: Optional[UUID] = None
    team2_id: Optional[UUID] = None
    player1_id: Optional[UUID] = None
    player2_id: Optional[UUID] = None
    scheduled_time: datetime.datetime
    actual_time: Optional[datetime.datetime] = None
    court_id: Optional[UUID] = None
    status: GameStatusEnum
    duration_minutes: Optional[int] = None
