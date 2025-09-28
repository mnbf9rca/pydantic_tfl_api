from pydantic import RootModel, ConfigDict
from typing import Any


class GenericResponseModel(RootModel[Any]):

    model_config = ConfigDict(arbitrary_types_allowed=True)
