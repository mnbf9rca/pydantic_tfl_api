from pydantic import RootModel, ConfigDict
from typing import List
from .BikePointOccupancy import BikePointOccupancy


class BikePointOccupancyArray(RootModel[list[BikePointOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
