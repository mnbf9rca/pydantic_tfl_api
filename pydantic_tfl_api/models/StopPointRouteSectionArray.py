from pydantic import RootModel, ConfigDict
from typing import List
from .StopPointRouteSection import StopPointRouteSection


class StopPointRouteSectionArray(RootModel[List[StopPointRouteSection]]):

    model_config = ConfigDict(from_attributes=True)
