from pydantic import RootModel
from typing import List
from .ActiveServiceType import ActiveServiceType


class ActiveServiceTypesArray(RootModel[List[ActiveServiceType]]):
    class Config:
        from_attributes = True

