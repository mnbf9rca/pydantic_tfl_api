from pydantic import RootModel, ConfigDict
from typing import Any


class StringsArray(RootModel[list[Any]]):

    model_config = ConfigDict(from_attributes=True)
