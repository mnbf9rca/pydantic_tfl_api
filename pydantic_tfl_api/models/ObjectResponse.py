from pydantic import RootModel
from typing import Any, Dict


class ObjectResponse(RootModel[Dict[str, Any]]):

    model_config = {'from_attributes': True}
