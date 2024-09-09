from pydantic import RootModel
from typing import Any, Dict


class ObjectResponse(RootModel[Dict[str, Any]]):
    class Config:
        from_attributes = True

