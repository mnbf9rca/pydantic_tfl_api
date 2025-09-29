from pydantic import BaseModel, ConfigDict, Field


class AdditionalProperties(BaseModel):
    category: str | None = Field(None)
    key: str | None = Field(None)
    sourceSystemKey: str | None = Field(None)
    value: str | None = Field(None)
    modified: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
