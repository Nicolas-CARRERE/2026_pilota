'''
This file contains the Pydantic models for competitions and seasons.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enums import CompetitionStatusEnum
import datetime

class CompetitionYear(BaseModel):
    id: UUID
    year: int
    is_current: bool = False
