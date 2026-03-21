'''
This file contains the Pydantic models for reference data.
'''
from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from enums import GenderEnum, CompetitionTypeEnum
class AgeCategory(BaseModel):
    id: UUID
    name: str  # e.g., Poussins, Minimes, Seniors
    short_name: Optional[str] = None
    min_age: Optional[int] = None
    max_age: Optional[int] = None
    gender: Optional[GenderEnum] = None
    description: Optional[str] = None

class CompetitionGender(BaseModel):
    id: UUID
    name: str  # "Men", "Women", "Mixed"
    code: str  # "M", "F", "X"
    description: Optional[str] = None

class Modality(BaseModel):
    """
    Broad grouping like Bare hands, Cesta Punta, Paleta Goma, Xare, etc.
    Can match what FIPV / FFPB define as 'modalities'. :contentReference[oaicite:0]{index=0}
    """
    id: UUID
    name: str
    description: Optional[str] = None

class Discipline(BaseModel):
    """
    A specific version played under one modality,
    potentially with age/gender constraints.
    Example: Cesta Punta 2v2 Mur A Gauche, Paleta Goma Trinquet, etc.
    """
    id: UUID
    name: str
    modality_id: UUID
    gender: Optional[GenderEnum] = None
    description: Optional[str] = None
    # If categories differ per discipline, link age category:
    age_category_id: Optional[UUID] = None

class CompetitionSeries(BaseModel):
    """
    A logical grouping of recurring competitions.
    Provides normalized naming across years.
    e.g., 'France Nationale A de Grand Chistera'. :contentReference[oaicite:1]{index=1}
    """
    id: UUID
    code: str  # e.g., 'FR_NA_GC'
    name: str
    description: Optional[str] = None
    competition_type: CompetitionTypeEnum
