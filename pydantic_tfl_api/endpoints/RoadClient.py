from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import (
    Object,
    RoadCorridorsArray,
    RoadDisruption,
    RoadDisruptionsArray,
    StatusSeveritiesArray,
    StringsArray,
)
from .RoadClient_config import base_url, endpoints


class RoadClient(Client):
    """APIs relating to Road and similar services"""

    def Get(self, ) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets all roads managed by TfL

  Query path: `/Road/`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_Get'], endpoint_args=None)

    def GetByPathIds(self, ids: str) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets the road with the specified id (e.g. A1)

  Query path: `/Road/{ids}`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A1`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_GetByPathIds'], params=[ids], endpoint_args=None)

    def StatusByPathIdsQueryStartDateQueryEndDate(self, ids: str, startDate: str | None = None, endDate: str | None = None) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets the specified roads with the status aggregated over the date range specified, or now until the end of today if no dates are passed.

  Query path: `/Road/{ids}/Status`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" or use "all" to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A2`
    `startDate`: str - Format - date-time (as date-time in RFC3339). The start date to aggregate status from.
    `endDate`: str - Format - date-time (as date-time in RFC3339). The end date to aggregate status up to.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_StatusByPathIdsQueryStartDateQueryEndDate'], params=[ids], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    def DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery(self, ids: str, stripContent: bool | None = None, severities: list | None = None, categories: list | None = None, closures: bool | None = None) -> ResponseModel[RoadDisruptionsArray] | ApiError:
        '''
        Get active disruptions, filtered by road ids

  Query path: `/Road/{ids}/Disruption`

  `ResponseModel.content` contains `models.RoadDisruptionsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" use all for all to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A406`
    `stripContent`: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location, comments and streets.
    `severities`: list - an optional list of Severity names to filter on (a valid list of severities can be obtained from the /Road/Meta/severities endpoint).
    `categories`: list - an optional list of category names to filter on (a valid list of categories can be obtained from the /Road/Meta/categories endpoint).
    `closures`: bool - Optional, defaults to true. When true, always includes disruptions that have road closures, regardless of the severity filter. When false, the severity filter works as normal..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery'], params=[ids], endpoint_args={ 'stripContent': stripContent, 'severities': severities, 'categories': categories, 'closures': closures })

    def DisruptedStreetsByQueryStartDateQueryEndDate(self, startDate: str | None = None, endDate: str | None = None) -> ResponseModel[Object] | ApiError:
        '''
        Gets a list of disrupted streets. If no date filters are provided, current disruptions are returned.

  Query path: `/Road/all/Street/Disruption`

  `ResponseModel.content` contains `models.Object` type.


  Parameters:
    `startDate`: str - Format - date-time (as date-time in RFC3339). Optional, the start time to filter on.. Example: `2024-03-01`
    `endDate`: str - Format - date-time (as date-time in RFC3339). Optional, The end time to filter on.. Example: `2024-03-31`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_DisruptedStreetsByQueryStartDateQueryEndDate'], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    def DisruptionByIdByPathDisruptionIdsQueryStripContent(self, disruptionIds: str, stripContent: bool | None = None) -> ResponseModel[RoadDisruption] | ApiError:
        '''
        Gets a list of active disruptions filtered by disruption Ids.

  Query path: `/Road/all/Disruption/{disruptionIds}`

  `ResponseModel.content` contains `models.RoadDisruption` type.


  Parameters:
    `disruptionIds`: str - Comma-separated list of disruption identifiers to filter by.. Example: `TIMS-89632`
    `stripContent`: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location and comments..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_DisruptionByIdByPathDisruptionIdsQueryStripContent'], params=[disruptionIds], endpoint_args={ 'stripContent': stripContent })

    def MetaCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid RoadDisruption categories

  Query path: `/Road/Meta/Categories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_MetaCategories'], endpoint_args=None)

    def MetaSeverities(self, ) -> ResponseModel[StatusSeveritiesArray] | ApiError:
        '''
        Gets a list of valid RoadDisruption severity codes

  Query path: `/Road/Meta/Severities`

  `ResponseModel.content` contains `models.StatusSeveritiesArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Road_MetaSeverities'], endpoint_args=None)


class AsyncRoadClient(AsyncClient):
    """APIs relating to Road and similar services"""

    async def Get(self, ) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets all roads managed by TfL

  Query path: `/Road/`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_Get'], endpoint_args=None)

    async def GetByPathIds(self, ids: str) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets the road with the specified id (e.g. A1)

  Query path: `/Road/{ids}`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A1`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_GetByPathIds'], params=[ids], endpoint_args=None)

    async def StatusByPathIdsQueryStartDateQueryEndDate(self, ids: str, startDate: str | None = None, endDate: str | None = None) -> ResponseModel[RoadCorridorsArray] | ApiError:
        '''
        Gets the specified roads with the status aggregated over the date range specified, or now until the end of today if no dates are passed.

  Query path: `/Road/{ids}/Status`

  `ResponseModel.content` contains `models.RoadCorridorsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" or use "all" to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A2`
    `startDate`: str - Format - date-time (as date-time in RFC3339). The start date to aggregate status from.
    `endDate`: str - Format - date-time (as date-time in RFC3339). The end date to aggregate status up to.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_StatusByPathIdsQueryStartDateQueryEndDate'], params=[ids], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    async def DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery(self, ids: str, stripContent: bool | None = None, severities: list | None = None, categories: list | None = None, closures: bool | None = None) -> ResponseModel[RoadDisruptionsArray] | ApiError:
        '''
        Get active disruptions, filtered by road ids

  Query path: `/Road/{ids}/Disruption`

  `ResponseModel.content` contains `models.RoadDisruptionsArray` type.


  Parameters:
    `ids`: str - Comma-separated list of road identifiers e.g. "A406, A2" use all for all to ignore id filter (a full list of supported road identifiers can be found at the /Road/ endpoint). Example: `A406`
    `stripContent`: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location, comments and streets.
    `severities`: list - an optional list of Severity names to filter on (a valid list of severities can be obtained from the /Road/Meta/severities endpoint).
    `categories`: list - an optional list of category names to filter on (a valid list of categories can be obtained from the /Road/Meta/categories endpoint).
    `closures`: bool - Optional, defaults to true. When true, always includes disruptions that have road closures, regardless of the severity filter. When false, the severity filter works as normal..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery'], params=[ids], endpoint_args={ 'stripContent': stripContent, 'severities': severities, 'categories': categories, 'closures': closures })

    async def DisruptedStreetsByQueryStartDateQueryEndDate(self, startDate: str | None = None, endDate: str | None = None) -> ResponseModel[Object] | ApiError:
        '''
        Gets a list of disrupted streets. If no date filters are provided, current disruptions are returned.

  Query path: `/Road/all/Street/Disruption`

  `ResponseModel.content` contains `models.Object` type.


  Parameters:
    `startDate`: str - Format - date-time (as date-time in RFC3339). Optional, the start time to filter on.. Example: `2024-03-01`
    `endDate`: str - Format - date-time (as date-time in RFC3339). Optional, The end time to filter on.. Example: `2024-03-31`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_DisruptedStreetsByQueryStartDateQueryEndDate'], endpoint_args={ 'startDate': startDate, 'endDate': endDate })

    async def DisruptionByIdByPathDisruptionIdsQueryStripContent(self, disruptionIds: str, stripContent: bool | None = None) -> ResponseModel[RoadDisruption] | ApiError:
        '''
        Gets a list of active disruptions filtered by disruption Ids.

  Query path: `/Road/all/Disruption/{disruptionIds}`

  `ResponseModel.content` contains `models.RoadDisruption` type.


  Parameters:
    `disruptionIds`: str - Comma-separated list of disruption identifiers to filter by.. Example: `TIMS-89632`
    `stripContent`: bool - Optional, defaults to false. When true, removes every property/node except for id, point, severity, severityDescription, startDate, endDate, corridor details, location and comments..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_DisruptionByIdByPathDisruptionIdsQueryStripContent'], params=[disruptionIds], endpoint_args={ 'stripContent': stripContent })

    async def MetaCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid RoadDisruption categories

  Query path: `/Road/Meta/Categories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_MetaCategories'], endpoint_args=None)

    async def MetaSeverities(self, ) -> ResponseModel[StatusSeveritiesArray] | ApiError:
        '''
        Gets a list of valid RoadDisruption severity codes

  Query path: `/Road/Meta/Severities`

  `ResponseModel.content` contains `models.StatusSeveritiesArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Road_MetaSeverities'], endpoint_args=None)

