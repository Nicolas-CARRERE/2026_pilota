'''
This file contains the Pydantic models for organizers.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enums import OrganizerTypeEnum

class Organizer(BaseModel):
    id: UUID
    name: str
    short_name: Optional[str] = None
    country: Optional[str] = None
    type: OrganizerTypeEnum
    founded_year: Optional[int] = None
    website: Optional[str] = None
    is_active: bool = True
