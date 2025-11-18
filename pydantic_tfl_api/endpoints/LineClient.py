from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import (
    DisruptionArray,
    LineArray,
    ModeArray,
    ObjectResponse,
    PredictionArray,
    RouteSearchResponse,
    RouteSequence,
    StatusSeveritiesArray,
    StopPointArray,
    StringsArray,
    TimetableResponse,
)
from .LineClient_config import base_url, endpoints


class LineClient(Client):
    """APIs relating to Line and similar services"""

    def MetaModes(self, ) -> ResponseModel[ModeArray] | ApiError:
        '''
        Gets a list of valid modes

  Query path: `/Line/Meta/Modes`

  `ResponseModel.content` contains `models.ModeArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaModes'], endpoint_args=None)

    def MetaSeverity(self, ) -> ResponseModel[StatusSeveritiesArray] | ApiError:
        '''
        Gets a list of valid severity codes

  Query path: `/Line/Meta/Severity`

  `ResponseModel.content` contains `models.StatusSeveritiesArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaSeverity'], endpoint_args=None)

    def MetaDisruptionCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid disruption categories

  Query path: `/Line/Meta/DisruptionCategories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaDisruptionCategories'], endpoint_args=None)

    def MetaServiceTypes(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid ServiceTypes to filter on

  Query path: `/Line/Meta/ServiceTypes`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaServiceTypes'], endpoint_args=None)

    def GetByPathIds(self, ids: str) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets lines that match the specified line ids.

  Query path: `/Line/{ids}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_GetByPathIds'], params=[ids], endpoint_args=None)

    def GetByModeByPathModes(self, modes: str) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets lines that serve the given modes.

  Query path: `/Line/Mode/{modes}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_GetByModeByPathModes'], params=[modes], endpoint_args=None)

    def RouteByQueryServiceTypes(self, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Get all valid routes for all lines, including the name and id of the originating and terminating stops for each route.

  Query path: `/Line/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteByQueryServiceTypes'], endpoint_args={ 'serviceTypes': serviceTypes })

    def LineRoutesByIdsByPathIdsQueryServiceTypes(self, ids: str, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Get all valid routes for given line ids, including the name and id of the originating and terminating stops for each route.

  Query path: `/Line/{ids}/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_LineRoutesByIdsByPathIdsQueryServiceTypes'], params=[ids], endpoint_args={ 'serviceTypes': serviceTypes })

    def RouteByModeByPathModesQueryServiceTypes(self, modes: str, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets all lines and their valid routes for given modes, including the name and id of the originating and terminating stops for each route

  Query path: `/Line/Mode/{modes}/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteByModeByPathModesQueryServiceTypes'], params=[modes], endpoint_args={ 'serviceTypes': serviceTypes })

    def RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding(self, id: str, direction: str, serviceTypes: str | None = None, excludeCrowding: bool | None = None) -> ResponseModel[RouteSequence] | ApiError:
        '''
        Gets all valid routes for given line id, including the sequence of stops on each route.

  Query path: `/Line/{id}/Route/Sequence/{direction}`

  `ResponseModel.content` contains `models.RouteSequence` type.


  Parameters:
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `direction`: str - The direction of travel. Can be inbound or outbound.. Example: `inbound`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
    `excludeCrowding`: bool - That excludes crowding from line disruptions. Can be true or false..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding'], params=[id, direction], endpoint_args={ 'serviceTypes': serviceTypes, 'excludeCrowding': excludeCrowding })

    def StatusByPathIdsPathStartDatePathEndDateQueryDetail(self, ids: str, startDate: str, endDate: str, detail: bool | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status for given line ids during the provided dates e.g Minor Delays

  Query path: `/Line/{ids}/Status/{startDate}/to/{endDate}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `startDate`: str - Format - date-time (as date-time in RFC3339). Start date for start of the period. Example: `2024-03-01`
    `endDate`: str - Format - date-time (as date-time in RFC3339). End date for the period that the disruption will fall within to be included in the results. Example: `2024-03-31`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByPathIdsPathStartDatePathEndDateQueryDetail'], params=[ids, startDate, endDate], endpoint_args={ 'detail': detail })

    def StatusByIdsByPathIdsQueryDetail(self, ids: str, detail: bool | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status of for given line ids e.g Minor Delays

  Query path: `/Line/{ids}/Status`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByIdsByPathIdsQueryDetail'], params=[ids], endpoint_args={ 'detail': detail })

    def SearchByPathQueryQueryModesQueryServiceTypes(self, query: str, modes: list | None = None, serviceTypes: str | None = None) -> ResponseModel[RouteSearchResponse] | ApiError:
        '''
        Search for lines or routes matching the query string

  Query path: `/Line/Search/{query}`

  `ResponseModel.content` contains `models.RouteSearchResponse` type.


  Parameters:
    `query`: str - Search term e.g victoria. Example: `victoria`
    `modes`: list - Optionally filter by the specified modes.
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_SearchByPathQueryQueryModesQueryServiceTypes'], params=[query], endpoint_args={ 'modes': modes, 'serviceTypes': serviceTypes })

    def StatusBySeverityByPathSeverity(self, severity: int) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status for all lines with a given severity A list of valid severity codes can be obtained from a call to Line/Meta/Severity

  Query path: `/Line/Status/{severity}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `severity`: int - Format - int32. The level of severity (eg: a number from 0 to 14). Example: `2`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusBySeverityByPathSeverity'], params=[severity], endpoint_args=None)

    def StatusByModeByPathModesQueryDetailQuerySeverityLevel(self, modes: str, detail: bool | None = None, severityLevel: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status of for all lines for the given modes

  Query path: `/Line/Mode/{modes}/Status`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes to filter by. e.g. tube,dlr. Example: `tube`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
    `severityLevel`: str - If specified, ensures that only those line status(es) are returned within the lines that have disruptions with the matching severity level..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel'], params=[modes], endpoint_args={ 'detail': detail, 'severityLevel': severityLevel })

    def StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly(self, id: str, tflOperatedNationalRailStationsOnly: bool | None = None) -> ResponseModel[StopPointArray] | ApiError:
        '''
        Gets a list of the stations that serve the given line id

  Query path: `/Line/{id}/StopPoints`

  `ResponseModel.content` contains `models.StopPointArray` type.


  Parameters:
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `tflOperatedNationalRailStationsOnly`: bool - If the national-rail line is requested, this flag will filter the national rail stations so that only those operated by TfL are returned.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly'], params=[id], endpoint_args={ 'tflOperatedNationalRailStationsOnly': tflOperatedNationalRailStationsOnly })

    def TimetableByPathFromStopPointIdPathId(self, fromStopPointId: str, id: str) -> ResponseModel[TimetableResponse] | ApiError:
        '''
        Gets the timetable for a specified station on the give line

  Query path: `/Line/{id}/Timetable/{fromStopPointId}`

  `ResponseModel.content` contains `models.TimetableResponse` type.


  Parameters:
    `fromStopPointId`: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `id`: str - A single line id e.g. victoria. Example: `victoria`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_TimetableByPathFromStopPointIdPathId'], params=[fromStopPointId, id], endpoint_args=None)

    def TimetableToByPathFromStopPointIdPathIdPathToStopPointId(self, fromStopPointId: str, id: str, toStopPointId: str) -> ResponseModel[TimetableResponse] | ApiError:
        '''
        Gets the timetable for a specified station on the give line with specified destination

  Query path: `/Line/{id}/Timetable/{fromStopPointId}/to/{toStopPointId}`

  `ResponseModel.content` contains `models.TimetableResponse` type.


  Parameters:
    `fromStopPointId`: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `toStopPointId`: str - The destination stations's Naptan code. Example: `940GZZLUGPK`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_TimetableToByPathFromStopPointIdPathIdPathToStopPointId'], params=[fromStopPointId, id, toStopPointId], endpoint_args=None)

    def DisruptionByPathIds(self, ids: str) -> ResponseModel[DisruptionArray] | ApiError:
        '''
        Get disruptions for the given line ids

  Query path: `/Line/{ids}/Disruption`

  `ResponseModel.content` contains `models.DisruptionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByPathIds'], params=[ids], endpoint_args=None)

    def DisruptionByModeByPathModes(self, modes: str) -> ResponseModel[DisruptionArray] | ApiError:
        '''
        Get disruptions for all lines of the given modes.

  Query path: `/Line/Mode/{modes}/Disruption`

  `ResponseModel.content` contains `models.DisruptionArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByModeByPathModes'], params=[modes], endpoint_args=None)

    def ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina(self, ids: str, stopPointId: str, direction: str | None = None, destinationStationId: str | None = None) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

  Query path: `/Line/{ids}/Arrivals/{stopPointId}`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `stopPointId`: str - Optional. Id of stop to get arrival predictions for (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `direction`: str - Optional. The direction of travel. Can be inbound or outbound or all. If left blank, and destinationStopId is set, will default to all.
    `destinationStationId`: str - Optional. Id of destination stop.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina'], params=[ids, stopPointId], endpoint_args={ 'direction': direction, 'destinationStationId': destinationStationId })

    def ArrivalsByPathIds(self, ids: str) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

  Query path: `/Line/{ids}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsByPathIds'], params=[ids], endpoint_args=None)

    def Proxy(self, ) -> ResponseModel[ObjectResponse] | ApiError:
        '''
        Forwards any remaining requests to the back-end

  Query path: `/Line/*`

  `ResponseModel.content` contains `models.ObjectResponse` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)


class AsyncLineClient(AsyncClient):
    """APIs relating to Line and similar services"""

    async def MetaModes(self, ) -> ResponseModel[ModeArray] | ApiError:
        '''
        Gets a list of valid modes

  Query path: `/Line/Meta/Modes`

  `ResponseModel.content` contains `models.ModeArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_MetaModes'], endpoint_args=None)

    async def MetaSeverity(self, ) -> ResponseModel[StatusSeveritiesArray] | ApiError:
        '''
        Gets a list of valid severity codes

  Query path: `/Line/Meta/Severity`

  `ResponseModel.content` contains `models.StatusSeveritiesArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_MetaSeverity'], endpoint_args=None)

    async def MetaDisruptionCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid disruption categories

  Query path: `/Line/Meta/DisruptionCategories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_MetaDisruptionCategories'], endpoint_args=None)

    async def MetaServiceTypes(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets a list of valid ServiceTypes to filter on

  Query path: `/Line/Meta/ServiceTypes`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_MetaServiceTypes'], endpoint_args=None)

    async def GetByPathIds(self, ids: str) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets lines that match the specified line ids.

  Query path: `/Line/{ids}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_GetByPathIds'], params=[ids], endpoint_args=None)

    async def GetByModeByPathModes(self, modes: str) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets lines that serve the given modes.

  Query path: `/Line/Mode/{modes}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_GetByModeByPathModes'], params=[modes], endpoint_args=None)

    async def RouteByQueryServiceTypes(self, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Get all valid routes for all lines, including the name and id of the originating and terminating stops for each route.

  Query path: `/Line/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_RouteByQueryServiceTypes'], endpoint_args={ 'serviceTypes': serviceTypes })

    async def LineRoutesByIdsByPathIdsQueryServiceTypes(self, ids: str, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Get all valid routes for given line ids, including the name and id of the originating and terminating stops for each route.

  Query path: `/Line/{ids}/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_LineRoutesByIdsByPathIdsQueryServiceTypes'], params=[ids], endpoint_args={ 'serviceTypes': serviceTypes })

    async def RouteByModeByPathModesQueryServiceTypes(self, modes: str, serviceTypes: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets all lines and their valid routes for given modes, including the name and id of the originating and terminating stops for each route

  Query path: `/Line/Mode/{modes}/Route`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_RouteByModeByPathModesQueryServiceTypes'], params=[modes], endpoint_args={ 'serviceTypes': serviceTypes })

    async def RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding(self, id: str, direction: str, serviceTypes: str | None = None, excludeCrowding: bool | None = None) -> ResponseModel[RouteSequence] | ApiError:
        '''
        Gets all valid routes for given line id, including the sequence of stops on each route.

  Query path: `/Line/{id}/Route/Sequence/{direction}`

  `ResponseModel.content` contains `models.RouteSequence` type.


  Parameters:
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `direction`: str - The direction of travel. Can be inbound or outbound.. Example: `inbound`
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
    `excludeCrowding`: bool - That excludes crowding from line disruptions. Can be true or false..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding'], params=[id, direction], endpoint_args={ 'serviceTypes': serviceTypes, 'excludeCrowding': excludeCrowding })

    async def StatusByPathIdsPathStartDatePathEndDateQueryDetail(self, ids: str, startDate: str, endDate: str, detail: bool | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status for given line ids during the provided dates e.g Minor Delays

  Query path: `/Line/{ids}/Status/{startDate}/to/{endDate}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `startDate`: str - Format - date-time (as date-time in RFC3339). Start date for start of the period. Example: `2024-03-01`
    `endDate`: str - Format - date-time (as date-time in RFC3339). End date for the period that the disruption will fall within to be included in the results. Example: `2024-03-31`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_StatusByPathIdsPathStartDatePathEndDateQueryDetail'], params=[ids, startDate, endDate], endpoint_args={ 'detail': detail })

    async def StatusByIdsByPathIdsQueryDetail(self, ids: str, detail: bool | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status of for given line ids e.g Minor Delays

  Query path: `/Line/{ids}/Status`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_StatusByIdsByPathIdsQueryDetail'], params=[ids], endpoint_args={ 'detail': detail })

    async def SearchByPathQueryQueryModesQueryServiceTypes(self, query: str, modes: list | None = None, serviceTypes: str | None = None) -> ResponseModel[RouteSearchResponse] | ApiError:
        '''
        Search for lines or routes matching the query string

  Query path: `/Line/Search/{query}`

  `ResponseModel.content` contains `models.RouteSearchResponse` type.


  Parameters:
    `query`: str - Search term e.g victoria. Example: `victoria`
    `modes`: list - Optionally filter by the specified modes.
    `serviceTypes`: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_SearchByPathQueryQueryModesQueryServiceTypes'], params=[query], endpoint_args={ 'modes': modes, 'serviceTypes': serviceTypes })

    async def StatusBySeverityByPathSeverity(self, severity: int) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status for all lines with a given severity A list of valid severity codes can be obtained from a call to Line/Meta/Severity

  Query path: `/Line/Status/{severity}`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `severity`: int - Format - int32. The level of severity (eg: a number from 0 to 14). Example: `2`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_StatusBySeverityByPathSeverity'], params=[severity], endpoint_args=None)

    async def StatusByModeByPathModesQueryDetailQuerySeverityLevel(self, modes: str, detail: bool | None = None, severityLevel: str | None = None) -> ResponseModel[LineArray] | ApiError:
        '''
        Gets the line status of for all lines for the given modes

  Query path: `/Line/Mode/{modes}/Status`

  `ResponseModel.content` contains `models.LineArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes to filter by. e.g. tube,dlr. Example: `tube`
    `detail`: bool - Include details of the disruptions that are causing the line status including the affected stops and routes.
    `severityLevel`: str - If specified, ensures that only those line status(es) are returned within the lines that have disruptions with the matching severity level..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel'], params=[modes], endpoint_args={ 'detail': detail, 'severityLevel': severityLevel })

    async def StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly(self, id: str, tflOperatedNationalRailStationsOnly: bool | None = None) -> ResponseModel[StopPointArray] | ApiError:
        '''
        Gets a list of the stations that serve the given line id

  Query path: `/Line/{id}/StopPoints`

  `ResponseModel.content` contains `models.StopPointArray` type.


  Parameters:
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `tflOperatedNationalRailStationsOnly`: bool - If the national-rail line is requested, this flag will filter the national rail stations so that only those operated by TfL are returned.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly'], params=[id], endpoint_args={ 'tflOperatedNationalRailStationsOnly': tflOperatedNationalRailStationsOnly })

    async def TimetableByPathFromStopPointIdPathId(self, fromStopPointId: str, id: str) -> ResponseModel[TimetableResponse] | ApiError:
        '''
        Gets the timetable for a specified station on the give line

  Query path: `/Line/{id}/Timetable/{fromStopPointId}`

  `ResponseModel.content` contains `models.TimetableResponse` type.


  Parameters:
    `fromStopPointId`: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `id`: str - A single line id e.g. victoria. Example: `victoria`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_TimetableByPathFromStopPointIdPathId'], params=[fromStopPointId, id], endpoint_args=None)

    async def TimetableToByPathFromStopPointIdPathIdPathToStopPointId(self, fromStopPointId: str, id: str, toStopPointId: str) -> ResponseModel[TimetableResponse] | ApiError:
        '''
        Gets the timetable for a specified station on the give line with specified destination

  Query path: `/Line/{id}/Timetable/{fromStopPointId}/to/{toStopPointId}`

  `ResponseModel.content` contains `models.TimetableResponse` type.


  Parameters:
    `fromStopPointId`: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `id`: str - A single line id e.g. victoria. Example: `victoria`
    `toStopPointId`: str - The destination stations's Naptan code. Example: `940GZZLUGPK`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_TimetableToByPathFromStopPointIdPathIdPathToStopPointId'], params=[fromStopPointId, id, toStopPointId], endpoint_args=None)

    async def DisruptionByPathIds(self, ids: str) -> ResponseModel[DisruptionArray] | ApiError:
        '''
        Get disruptions for the given line ids

  Query path: `/Line/{ids}/Disruption`

  `ResponseModel.content` contains `models.DisruptionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByPathIds'], params=[ids], endpoint_args=None)

    async def DisruptionByModeByPathModes(self, modes: str) -> ResponseModel[DisruptionArray] | ApiError:
        '''
        Get disruptions for all lines of the given modes.

  Query path: `/Line/Mode/{modes}/Disruption`

  `ResponseModel.content` contains `models.DisruptionArray` type.


  Parameters:
    `modes`: str - A comma-separated list of modes e.g. tube,dlr. Example: `tube`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByModeByPathModes'], params=[modes], endpoint_args=None)

    async def ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina(self, ids: str, stopPointId: str, direction: str | None = None, destinationStationId: str | None = None) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

  Query path: `/Line/{ids}/Arrivals/{stopPointId}`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
    `stopPointId`: str - Optional. Id of stop to get arrival predictions for (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: `940GZZLUVIC`
    `direction`: str - Optional. The direction of travel. Can be inbound or outbound or all. If left blank, and destinationStopId is set, will default to all.
    `destinationStationId`: str - Optional. Id of destination stop.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina'], params=[ids, stopPointId], endpoint_args={ 'direction': direction, 'destinationStationId': destinationStationId })

    async def ArrivalsByPathIds(self, ids: str) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

  Query path: `/Line/{ids}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: `victoria`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsByPathIds'], params=[ids], endpoint_args=None)

    async def Proxy(self, ) -> ResponseModel[ObjectResponse] | ApiError:
        '''
        Forwards any remaining requests to the back-end

  Query path: `/Line/*`

  `ResponseModel.content` contains `models.ObjectResponse` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)

