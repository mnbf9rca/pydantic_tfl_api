from pydantic import BaseModel, Field, ConfigDict


class PathAttribute(BaseModel):
    name: str | None = Field(None)
    value: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
