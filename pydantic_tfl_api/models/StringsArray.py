from pydantic import RootModel
from typing import Any, List


class StringsArray(RootModel[List[Any]]):

    model_config = {'from_attributes': True}
