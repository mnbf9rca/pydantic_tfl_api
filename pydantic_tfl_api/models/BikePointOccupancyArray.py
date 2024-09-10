from pydantic import RootModel
from typing import List
from .BikePointOccupancy import BikePointOccupancy


class BikePointOccupancyArray(RootModel[List[BikePointOccupancy]]):

    model_config = {'from_attributes': True}
