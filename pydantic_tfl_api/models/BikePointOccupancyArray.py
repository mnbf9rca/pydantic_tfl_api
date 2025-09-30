from pydantic import ConfigDict, RootModel

from .BikePointOccupancy import BikePointOccupancy


class BikePointOccupancyArray(RootModel[list[BikePointOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
