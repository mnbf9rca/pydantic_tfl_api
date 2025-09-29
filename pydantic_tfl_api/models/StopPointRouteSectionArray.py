from pydantic import RootModel, ConfigDict
from typing import List
from .StopPointRouteSection import StopPointRouteSection


class StopPointRouteSectionArray(RootModel[list[StopPointRouteSection]]):

    model_config = ConfigDict(from_attributes=True)
