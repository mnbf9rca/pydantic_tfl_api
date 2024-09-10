from .PhaseEnum import PhaseEnum
from pydantic import BaseModel, Field
from typing import List, Optional


class RoadProject(BaseModel):
    projectId: Optional[str] = Field(None, alias='projectId')
    schemeName: Optional[str] = Field(None, alias='schemeName')
    projectName: Optional[str] = Field(None, alias='projectName')
    projectDescription: Optional[str] = Field(None, alias='projectDescription')
    projectPageUrl: Optional[str] = Field(None, alias='projectPageUrl')
    consultationPageUrl: Optional[str] = Field(None, alias='consultationPageUrl')
    consultationStartDate: Optional[str] = Field(None, alias='consultationStartDate')
    consultationEndDate: Optional[str] = Field(None, alias='consultationEndDate')
    constructionStartDate: Optional[str] = Field(None, alias='constructionStartDate')
    constructionEndDate: Optional[str] = Field(None, alias='constructionEndDate')
    boroughsBenefited: Optional[list[str]] = Field(None, alias='boroughsBenefited')
    cycleSuperhighwayId: Optional[str] = Field(None, alias='cycleSuperhighwayId')
    phase: Optional[PhaseEnum] = Field(None, alias='phase')
    contactName: Optional[str] = Field(None, alias='contactName')
    contactEmail: Optional[str] = Field(None, alias='contactEmail')
    externalPageUrl: Optional[str] = Field(None, alias='externalPageUrl')
    projectSummaryPageUrl: Optional[str] = Field(None, alias='projectSummaryPageUrl')

    model_config = {'from_attributes': True}
