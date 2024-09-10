from pydantic import RootModel
from typing import List
from .StopPointRouteSection import StopPointRouteSection


class StopPointRouteSectionArray(RootModel[List[StopPointRouteSection]]):

    model_config = {'from_attributes': True}
