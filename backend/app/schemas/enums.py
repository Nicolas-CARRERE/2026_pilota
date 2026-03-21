'''
This file contains the Pydantic enums for the player schema.
'''
from enum import Enum

class GenderEnum(str, Enum):
    M = "M"
    F = "F"
    X = "X"  # Mixed or open

class CompetitionTypeEnum(str, Enum):
    league = "league"
    tournament = "tournament"

class OrganizerTypeEnum(str, Enum):
    committee = "committee"
    league = "league"
    federation = "federation"
    club = "club"

class ScrapeFrequencyEnum(str, Enum):
    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    as_needed = "as_needed"

class CompetitionStatusEnum(str, Enum):
    upcoming = "upcoming"
    ongoing = "ongoing"
    completed = "completed"
    cancelled = "cancelled"

class GameStatusEnum(str, Enum):
    scheduled = "scheduled"
    in_progress = "in_progress"
    completed = "completed"
    postponed = "postponed"
    cancelled = "cancelled"

class CourtType(str, Enum):
    FRONTON = "fronton"
    TRINQUET = "trinquet"
    MUR_A_GAUCHE = "mur_a_gauche"
    PLACE_LIBRE = "place_libre"  # e.g. jaialai long court
