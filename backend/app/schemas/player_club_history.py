'''
This file contains the Pydantic models for players, clubs, and teams.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
import datetime


class PlayerClubHistory(BaseModel):
    """
    Tracks which club a player belongs to for eligibility/statistics,
    can overlap seasons.
    """
    id: UUID
    player_id: UUID
    club_id: UUID
    start_date: datetime.date
    end_date: Optional[datetime.date]
