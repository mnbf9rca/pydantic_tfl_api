from .StopPointRouteSection import StopPointRouteSection
from pydantic import RootModel, ConfigDict


class StopPointRouteSectionArray(RootModel[list[StopPointRouteSection]]):

    model_config = ConfigDict(from_attributes=True)
