from typing import Any

from pydantic import ConfigDict, RootModel


class StringsArray(RootModel[list[Any]]):

    model_config = ConfigDict(from_attributes=True)
