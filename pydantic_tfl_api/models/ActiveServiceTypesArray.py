from pydantic import ConfigDict, RootModel

from .ActiveServiceType import ActiveServiceType


class ActiveServiceTypesArray(RootModel[list[ActiveServiceType]]):

    model_config = ConfigDict(from_attributes=True)
