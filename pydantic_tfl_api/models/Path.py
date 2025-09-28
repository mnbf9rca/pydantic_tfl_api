from .Identifier import Identifier
from .JpElevation import JpElevation
from pydantic import BaseModel, Field, ConfigDict


class Path(BaseModel):
    lineString: str | None = Field(None)
    stopPoints: list[Identifier] | None = Field(None)
    elevation: list[JpElevation] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
