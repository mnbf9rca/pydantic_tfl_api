from pydantic import RootModel
from typing import List
from .ActiveServiceType import ActiveServiceType


class ActiveServiceTypesArray(RootModel[List[ActiveServiceType]]):

    model_config = {'from_attributes': True}
