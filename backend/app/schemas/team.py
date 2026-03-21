'''
This file contains the Pydantic models for players, clubs, and teams.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class Team(BaseModel):
    id: UUID
    club_id: Optional[UUID]  # link to a club
    name: str
    short_name: Optional[str] = None
    discipline_id: UUID
    is_professional: bool = False
