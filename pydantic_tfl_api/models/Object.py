from typing import Any

from pydantic import ConfigDict, RootModel


class Object(RootModel[dict[str, Any]]):

    model_config = ConfigDict(from_attributes=True)
