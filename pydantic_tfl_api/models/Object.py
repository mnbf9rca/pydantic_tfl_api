from pydantic import RootModel, ConfigDict
from typing import Any


class Object(RootModel[dict[str, Any]]):

    model_config = ConfigDict(from_attributes=True)
