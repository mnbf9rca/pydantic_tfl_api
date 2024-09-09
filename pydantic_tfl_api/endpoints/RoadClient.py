from ..client import Client
from .RoadClient_config import endpoints
from .. import models
from ..models import ApiError

class RoadClient(Client):
    def get(self, ) -> models.RoadCorridorsArray | ApiError:
        '''
        Gets all roads managed by TfL

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Road_Get'], endpoint_args=None)

    def getbypathids(self, ids: str) -> models.RoadCorridorsArray | ApiError:
        '''
        Gets the road with the specified id (e.g. A1)

        Parameters:
        ids: str - Comma-separated list of road identifiers e.g. "A406, A2" (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: A1
        '''
        return self._send_request_and_deserialize(endpoints['Road_GetByPathIds'], params=[ids], endpoint_args=None)

    def statusbypathidsquerystartdatequeryenddate(self, ids: str, startDate: str | None = None, endDate: str | None = None) -> models.RoadCorridorsArray | ApiError:
        '''
        Gets the specified roads with the status aggregated over the date range specified, or now until the end of today if no dates are passed.

        Parameters:
        ids: str - Comma-separated list of road identifiers e.g. "A406, A2" or use "all" to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: A2
        startDate: str - Format - date-time (as date-time in RFC3339). The start date to aggregate status from. Example: None given
        endDate: str - Format - date-time (as date-time in RFC3339). The end date to aggregate status up to. Example: None given
        '''
        return self._send_request_and_deserialize(endpoints['Road_StatusByPathIdsQueryStartDateQueryEndDate'], params=[ids], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    def disruptionbypathidsquerystripcontentqueryseveritiesquerycategoriesquery(self, ids: str, stripContent: bool | None = None, severities: list | None = None, categories: list | None = None, closures: bool | None = None) -> models.RoadDisruptionsArray | ApiError:
        '''
        Get active disruptions, filtered by road ids

        Parameters:
        ids: str - Comma-separated list of road identifiers e.g. "A406, A2" use all for all to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: A406
        stripContent: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location, comments and streets. Example: None given
        severities: list - an optional list of Severity names to filter on (a valid list of severities can be obtained from the /Road/Meta/severities endpoint). Example: None given
        categories: list - an optional list of category names to filter on (a valid list of categories can be obtained from the /Road/Meta/categories endpoint). Example: None given
        closures: bool - Optional, defaults to true. When true, always includes disruptions that have road closures, regardless of the severity filter. When false, the severity filter works as normal.. Example: None given
        '''
        return self._send_request_and_deserialize(endpoints['Road_DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery'], params=[ids], endpoint_args={ 'stripContent': stripContent, 'severities': severities, 'categories': categories, 'closures': closures })

    def disruptedstreetsbyquerystartdatequeryenddate(self, startDate: str | None = None, endDate: str | None = None) -> models.Object | ApiError:
        '''
        Gets a list of disrupted streets. If no date filters are provided, current disruptions are returned.

        Parameters:
        startDate: str - Format - date-time (as date-time in RFC3339). Optional, the start time to filter on.. Example: 2024-03-01
        endDate: str - Format - date-time (as date-time in RFC3339). Optional, The end time to filter on.. Example: 2024-03-31
        '''
        return self._send_request_and_deserialize(endpoints['Road_DisruptedStreetsByQueryStartDateQueryEndDate'], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    def disruptionbyidbypathdisruptionidsquerystripcontent(self, disruptionIds: str, stripContent: bool | None = None) -> models.RoadDisruption | ApiError:
        '''
        Gets a list of active disruptions filtered by disruption Ids.

        Parameters:
        disruptionIds: str - Comma-separated list of disruption identifiers to filter by.. Example: TIMS-89632
        stripContent: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location and comments.. Example: None given
        '''
        return self._send_request_and_deserialize(endpoints['Road_DisruptionByIdByPathDisruptionIdsQueryStripContent'], params=[disruptionIds], endpoint_args={ 'stripContent': stripContent })

    def metacategories(self, ) -> models.StringsArray | ApiError:
        '''
        Gets a list of valid RoadDisruption categories

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Road_MetaCategories'], endpoint_args=None)

    def metaseverities(self, ) -> models.StatusSeveritiesArray | ApiError:
        '''
        Gets a list of valid RoadDisruption severity codes

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Road_MetaSeverities'], endpoint_args=None)

