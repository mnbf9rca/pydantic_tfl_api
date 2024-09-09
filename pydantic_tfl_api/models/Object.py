from pydantic import RootModel
from typing import Any, Dict


class Object(RootModel[Dict[str, Any]]):
    class Config:
        from_attributes = True

