from pydantic import RootModel
from typing import Any


class GenericResponseModel(RootModel[Any]):

    class Config:
        from_attributes = True
