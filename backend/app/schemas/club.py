'''
This file contains the Pydantic models for players, clubs, and teams.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel

class Club(BaseModel):
    id: UUID
    name: str
    short_name: Optional[str] = None
    country: Optional[str] = None
    region: Optional[str] = None
    founded_year: Optional[int] = None
    website: Optional[str] = None
    is_active: bool = True
