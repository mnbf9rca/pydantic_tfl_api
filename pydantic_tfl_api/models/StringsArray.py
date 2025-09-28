from pydantic import RootModel, ConfigDict
from typing import Any, List


class StringsArray(RootModel[List[Any]]):

    model_config = ConfigDict(from_attributes=True)
