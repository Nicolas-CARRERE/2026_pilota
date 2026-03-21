'''
This file contains the Pydantic models for games and results.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class ScoreEntry(BaseModel):
    score_id: UUID
    set_number: Optional[int] = None
    team1_score: Optional[int] = None
    team2_score: Optional[int] = None
