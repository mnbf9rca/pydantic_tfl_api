from pydantic import BaseModel, Field, ConfigDict


class MatchedRouteSections(BaseModel):
    id: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
