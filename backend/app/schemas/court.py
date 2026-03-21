'''
This file contains the Pydantic models for courts and venues.
'''
from uuid import UUID
from pydantic import BaseModel
from enums import CourtType

class Court(BaseModel):
    id: UUID
    name: str
    city: str
    country: str
    court_type: CourtType
