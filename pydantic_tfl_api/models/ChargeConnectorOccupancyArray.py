from pydantic import ConfigDict, RootModel

from .ChargeConnectorOccupancy import ChargeConnectorOccupancy


class ChargeConnectorOccupancyArray(RootModel[list[ChargeConnectorOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
