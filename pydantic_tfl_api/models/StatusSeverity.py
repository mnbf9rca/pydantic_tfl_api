from pydantic import BaseModel, ConfigDict, Field


class StatusSeverity(BaseModel):
    modeName: str | None = Field(None)
    severityLevel: int | None = Field(None)
    description: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
