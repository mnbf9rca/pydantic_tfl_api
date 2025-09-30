from pydantic import BaseModel, ConfigDict, Field

from .DisambiguationOption import DisambiguationOption


class Disambiguation(BaseModel):
    disambiguationOptions: list[DisambiguationOption] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
