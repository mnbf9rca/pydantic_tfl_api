from pydantic import RootModel, ConfigDict
from typing import Any, Dict


class Object(RootModel[Dict[str, Any]]):

    model_config = ConfigDict(from_attributes=True)
