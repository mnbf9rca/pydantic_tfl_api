from pydantic import RootModel, ConfigDict
from typing import List
from .ChargeConnectorOccupancy import ChargeConnectorOccupancy


class ChargeConnectorOccupancyArray(RootModel[List[ChargeConnectorOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
