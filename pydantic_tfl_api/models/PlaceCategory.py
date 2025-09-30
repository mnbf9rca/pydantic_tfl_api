from pydantic import BaseModel, ConfigDict, Field


class PlaceCategory(BaseModel):
    category: str | None = Field(None)
    availableKeys: list[str] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
