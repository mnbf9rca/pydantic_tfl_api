from .BikePointOccupancy import BikePointOccupancy
from pydantic import RootModel, ConfigDict


class BikePointOccupancyArray(RootModel[list[BikePointOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
