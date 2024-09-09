from pydantic import RootModel
from typing import List
from .ChargeConnectorOccupancy import ChargeConnectorOccupancy


class ChargeConnectorOccupancyArray(RootModel[List[ChargeConnectorOccupancy]]):
    class Config:
        from_attributes = True

