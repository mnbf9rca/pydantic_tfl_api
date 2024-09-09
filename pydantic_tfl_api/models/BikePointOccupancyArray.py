from pydantic import RootModel
from typing import List
from .BikePointOccupancy import BikePointOccupancy


class BikePointOccupancyArray(RootModel[List[BikePointOccupancy]]):
    class Config:
        from_attributes = True

