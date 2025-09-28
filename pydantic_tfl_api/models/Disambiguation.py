from .DisambiguationOption import DisambiguationOption
from pydantic import BaseModel, Field, ConfigDict


class Disambiguation(BaseModel):
    disambiguationOptions: list[DisambiguationOption] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
