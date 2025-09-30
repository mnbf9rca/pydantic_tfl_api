from pydantic import ConfigDict, RootModel

from .StopPointRouteSection import StopPointRouteSection


class StopPointRouteSectionArray(RootModel[list[StopPointRouteSection]]):

    model_config = ConfigDict(from_attributes=True)
