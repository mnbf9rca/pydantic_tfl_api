from pydantic import RootModel, ConfigDict
from typing import List
from .BikePointOccupancy import BikePointOccupancy


class BikePointOccupancyArray(RootModel[List[BikePointOccupancy]]):

    model_config = ConfigDict(from_attributes=True)
