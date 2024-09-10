from pydantic import RootModel
from typing import List
from .ChargeConnectorOccupancy import ChargeConnectorOccupancy


class ChargeConnectorOccupancyArray(RootModel[List[ChargeConnectorOccupancy]]):

    model_config = {'from_attributes': True}
