from .Identifier import Identifier
from .JpElevation import JpElevation
from pydantic import BaseModel, Field
from typing import List, Optional


class Path(BaseModel):
    lineString: Optional[str] = Field(None, alias='lineString')
    stopPoints: Optional[list[Identifier]] = Field(None, alias='stopPoints')
    elevation: Optional[list[JpElevation]] = Field(None, alias='elevation')

    model_config = {'from_attributes': True}
