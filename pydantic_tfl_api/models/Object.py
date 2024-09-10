from pydantic import RootModel
from typing import Any, Dict


class Object(RootModel[Dict[str, Any]]):

    model_config = {'from_attributes': True}
