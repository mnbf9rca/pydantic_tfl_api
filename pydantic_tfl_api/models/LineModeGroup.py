from pydantic import BaseModel, ConfigDict, Field


class LineModeGroup(BaseModel):
    modeName: str | None = Field(None)
    lineIdentifier: list[str] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
