from pydantic import RootModel, ConfigDict
from .ActiveServiceType import ActiveServiceType


class ActiveServiceTypesArray(RootModel[list[ActiveServiceType]]):

    model_config = ConfigDict(from_attributes=True)
