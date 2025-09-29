from pydantic import RootModel, ConfigDict
from typing import Any, Dict


class ObjectResponse(RootModel[dict[str, Any]]):

    model_config = ConfigDict(from_attributes=True)
