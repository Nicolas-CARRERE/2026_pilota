'''
This file contains the Pydantic models for competitions and seasons.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enums import CompetitionStatusEnum
import datetime

class Competition(BaseModel):
    """
    A specific edition in time of a series.
    A series can have many competitions over years.
    """
    id: UUID
    series_id: Optional[UUID] = None  # links to series
    discipline_id: UUID
    year_id: UUID
    organizer_id: UUID
    age_category_id: Optional[UUID] = None
    gender_id: Optional[UUID] = None
    start_date: datetime.date
    end_date: Optional[datetime.date] = None
    location: Optional[str] = None
    country: Optional[str] = None
    status: CompetitionStatusEnum
    # Optional phase (group, finals):
    phase: Optional[str] = None
