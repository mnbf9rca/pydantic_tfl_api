from pydantic import BaseModel, ConfigDict, Field

from .PhaseEnum import PhaseEnum


class RoadProject(BaseModel):
    projectId: str | None = Field(None)
    schemeName: str | None = Field(None)
    projectName: str | None = Field(None)
    projectDescription: str | None = Field(None)
    projectPageUrl: str | None = Field(None)
    consultationPageUrl: str | None = Field(None)
    consultationStartDate: str | None = Field(None)
    consultationEndDate: str | None = Field(None)
    constructionStartDate: str | None = Field(None)
    constructionEndDate: str | None = Field(None)
    boroughsBenefited: list[str] | None = Field(None)
    cycleSuperhighwayId: str | None = Field(None)
    phase: PhaseEnum | None = Field(None)
    contactName: str | None = Field(None)
    contactEmail: str | None = Field(None)
    externalPageUrl: str | None = Field(None)
    projectSummaryPageUrl: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
