from pydantic import BaseModel, ConfigDict, Field


class MatchedRouteSections(BaseModel):
    id: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
