'''
This file contains the Pydantic models for players, clubs, and teams.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
import datetime

class Player(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    nickname: Optional[str] = None
    birth_date: Optional[datetime.date] = None
    country: Optional[str] = None
    height_cm: Optional[int] = None
    weight_kg: Optional[int] = None
    dominant_hand: Optional[str] = None  # left, right
    is_active: bool = True
