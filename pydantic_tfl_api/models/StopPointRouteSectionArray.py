from pydantic import RootModel
from typing import List
from .StopPointRouteSection import StopPointRouteSection


class StopPointRouteSectionArray(RootModel[List[StopPointRouteSection]]):
    class Config:
        from_attributes = True

