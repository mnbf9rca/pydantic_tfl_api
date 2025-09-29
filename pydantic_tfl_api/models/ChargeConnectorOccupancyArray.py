from .ChargeConnectorOccupancy import ChargeConnectorOccupancy
from pydantic import RootModel, ConfigDict


class ChargeConnectorOccupancyArray(RootModel[list[ChargeConnectorOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
