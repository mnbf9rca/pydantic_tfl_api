from pydantic import RootModel
from typing import Any


class GenericResponseModel(RootModel[Any]):

    model_config = {'from_attributes': True}
