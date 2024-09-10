from .LineClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class LineClient(Client):
    def MetaModes(self, ) -> ResponseModel | ApiError:
        '''
        Gets a list of valid modes

        ResponseModel.content contains `models.ModeArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaModes'], endpoint_args=None)

    def MetaSeverity(self, ) -> ResponseModel | ApiError:
        '''
        Gets a list of valid severity codes

        ResponseModel.content contains `models.StatusSeveritiesArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaSeverity'], endpoint_args=None)

    def MetaDisruptionCategories(self, ) -> ResponseModel | ApiError:
        '''
        Gets a list of valid disruption categories

        ResponseModel.content contains `models.StringsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaDisruptionCategories'], endpoint_args=None)

    def MetaServiceTypes(self, ) -> ResponseModel | ApiError:
        '''
        Gets a list of valid ServiceTypes to filter on

        ResponseModel.content contains `models.StringsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_MetaServiceTypes'], endpoint_args=None)

    def GetByPathIds(self, ids: str) -> ResponseModel | ApiError:
        '''
        Gets lines that match the specified line ids.

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_GetByPathIds'], params=[ids], endpoint_args=None)

    def GetByModeByPathModes(self, modes: str) -> ResponseModel | ApiError:
        '''
        Gets lines that serve the given modes.

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        modes: str - A comma-separated list of modes e.g. tube,dlr. Example: tube
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_GetByModeByPathModes'], params=[modes], endpoint_args=None)

    def RouteByQueryServiceTypes(self, serviceTypes: str | None = None) -> ResponseModel | ApiError:
        '''
        Get all valid routes for all lines, including the name and id of the originating and terminating stops for each route.

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        serviceTypes: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteByQueryServiceTypes'], endpoint_args={ 'serviceTypes': serviceTypes })

    def LineRoutesByIdsByPathIdsQueryServiceTypes(self, ids: str, serviceTypes: str | None = None) -> ResponseModel | ApiError:
        '''
        Get all valid routes for given line ids, including the name and id of the originating and terminating stops for each route.

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        serviceTypes: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_LineRoutesByIdsByPathIdsQueryServiceTypes'], params=[ids], endpoint_args={ 'serviceTypes': serviceTypes })

    def RouteByModeByPathModesQueryServiceTypes(self, modes: str, serviceTypes: str | None = None) -> ResponseModel | ApiError:
        '''
        Gets all lines and their valid routes for given modes, including the name and id of the originating and terminating stops for each route

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        modes: str - A comma-separated list of modes e.g. tube,dlr. Example: tube
        serviceTypes: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteByModeByPathModesQueryServiceTypes'], params=[modes], endpoint_args={ 'serviceTypes': serviceTypes })

    def RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding(self, id: str, direction: str, serviceTypes: str | None = None, excludeCrowding: bool | None = None) -> ResponseModel | ApiError:
        '''
        Gets all valid routes for given line id, including the sequence of stops on each route.

        ResponseModel.content contains `models.RouteSequence` type.

        Parameters:
        id: str - A single line id e.g. victoria. Example: victoria
        direction: str - The direction of travel. Can be inbound or outbound.. Example: inbound
        serviceTypes: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified. Example: None given
        excludeCrowding: bool - That excludes crowding from line disruptions. Can be true or false.. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding'], params=[id, direction], endpoint_args={ 'serviceTypes': serviceTypes, 'excludeCrowding': excludeCrowding })

    def StatusByPathIdsPathStartDatePathEndDateQueryDetail(self, ids: str, startDate: str, endDate: str, detail: bool | None = None) -> ResponseModel | ApiError:
        '''
        Gets the line status for given line ids during the provided dates e.g Minor Delays

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        startDate: str - Format - date-time (as date-time in RFC3339). Start date for start of the period. Example: 2024-03-01
        endDate: str - Format - date-time (as date-time in RFC3339). End date for the period that the disruption will fall within to be included in the results. Example: 2024-03-31
        detail: bool - Include details of the disruptions that are causing the line status including the affected stops and routes. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByPathIdsPathStartDatePathEndDateQueryDetail'], params=[ids, startDate, endDate], endpoint_args={ 'detail': detail })

    def StatusByIdsByPathIdsQueryDetail(self, ids: str, detail: bool | None = None) -> ResponseModel | ApiError:
        '''
        Gets the line status of for given line ids e.g Minor Delays

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        detail: bool - Include details of the disruptions that are causing the line status including the affected stops and routes. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByIdsByPathIdsQueryDetail'], params=[ids], endpoint_args={ 'detail': detail })

    def SearchByPathQueryQueryModesQueryServiceTypes(self, query: str, modes: list | None = None, serviceTypes: str | None = None) -> ResponseModel | ApiError:
        '''
        Search for lines or routes matching the query string

        ResponseModel.content contains `models.RouteSearchResponse` type.

        Parameters:
        query: str - Search term e.g victoria. Example: victoria
        modes: list - Optionally filter by the specified modes. Example: None given
        serviceTypes: str - A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_SearchByPathQueryQueryModesQueryServiceTypes'], params=[query], endpoint_args={ 'modes': modes, 'serviceTypes': serviceTypes })

    def StatusBySeverityByPathSeverity(self, severity: int) -> ResponseModel | ApiError:
        '''
        Gets the line status for all lines with a given severity A list of valid severity codes can be obtained from a call to Line/Meta/Severity

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        severity: int - Format - int32. The level of severity (eg: a number from 0 to 14). Example: 2
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusBySeverityByPathSeverity'], params=[severity], endpoint_args=None)

    def StatusByModeByPathModesQueryDetailQuerySeverityLevel(self, modes: str, detail: bool | None = None, severityLevel: str | None = None) -> ResponseModel | ApiError:
        '''
        Gets the line status of for all lines for the given modes

        ResponseModel.content contains `models.LineArray` type.

        Parameters:
        modes: str - A comma-separated list of modes to filter by. e.g. tube,dlr. Example: tube
        detail: bool - Include details of the disruptions that are causing the line status including the affected stops and routes. Example: None given
        severityLevel: str - If specified, ensures that only those line status(es) are returned within the lines that have disruptions with the matching severity level.. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel'], params=[modes], endpoint_args={ 'detail': detail, 'severityLevel': severityLevel })

    def StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly(self, id: str, tflOperatedNationalRailStationsOnly: bool | None = None) -> ResponseModel | ApiError:
        '''
        Gets a list of the stations that serve the given line id

        ResponseModel.content contains `models.StopPointArray` type.

        Parameters:
        id: str - A single line id e.g. victoria. Example: victoria
        tflOperatedNationalRailStationsOnly: bool - If the national-rail line is requested, this flag will filter the national rail stations so that only those operated by TfL are returned. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly'], params=[id], endpoint_args={ 'tflOperatedNationalRailStationsOnly': tflOperatedNationalRailStationsOnly })

    def TimetableByPathFromStopPointIdPathId(self, fromStopPointId: str, id: str) -> ResponseModel | ApiError:
        '''
        Gets the timetable for a specified station on the give line

        ResponseModel.content contains `models.TimetableResponse` type.

        Parameters:
        fromStopPointId: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: 940GZZLUVIC
        id: str - A single line id e.g. victoria. Example: victoria
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_TimetableByPathFromStopPointIdPathId'], params=[fromStopPointId, id], endpoint_args=None)

    def TimetableToByPathFromStopPointIdPathIdPathToStopPointId(self, fromStopPointId: str, id: str, toStopPointId: str) -> ResponseModel | ApiError:
        '''
        Gets the timetable for a specified station on the give line with specified destination

        ResponseModel.content contains `models.TimetableResponse` type.

        Parameters:
        fromStopPointId: str - The originating station's stop point id (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: 940GZZLUVIC
        id: str - A single line id e.g. victoria. Example: victoria
        toStopPointId: str - The destination stations's Naptan code. Example: 940GZZLUGPK
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_TimetableToByPathFromStopPointIdPathIdPathToStopPointId'], params=[fromStopPointId, id, toStopPointId], endpoint_args=None)

    def DisruptionByPathIds(self, ids: str) -> ResponseModel | ApiError:
        '''
        Get disruptions for the given line ids

        ResponseModel.content contains `models.DisruptionArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByPathIds'], params=[ids], endpoint_args=None)

    def DisruptionByModeByPathModes(self, modes: str) -> ResponseModel | ApiError:
        '''
        Get disruptions for all lines of the given modes.

        ResponseModel.content contains `models.DisruptionArray` type.

        Parameters:
        modes: str - A comma-separated list of modes e.g. tube,dlr. Example: tube
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_DisruptionByModeByPathModes'], params=[modes], endpoint_args=None)

    def ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina(self, ids: str, stopPointId: str, direction: str | None = None, destinationStationId: str | None = None) -> ResponseModel | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

        ResponseModel.content contains `models.PredictionArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        stopPointId: str - Optional. Id of stop to get arrival predictions for (station naptan code e.g. 940GZZLUASL, you can use /StopPoint/Search/{query} endpoint to find a stop point id from a station name). Example: 940GZZLUVIC
        direction: str - Optional. The direction of travel. Can be inbound or outbound or all. If left blank, and destinationStopId is set, will default to all. Example: None given
        destinationStationId: str - Optional. Id of destination stop. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina'], params=[ids, stopPointId], endpoint_args={ 'direction': direction, 'destinationStationId': destinationStationId })

    def ArrivalsByPathIds(self, ids: str) -> ResponseModel | ApiError:
        '''
        Get the list of arrival predictions for given line ids based at the given stop

        ResponseModel.content contains `models.PredictionArray` type.

        Parameters:
        ids: str - A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.. Example: victoria
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Line_ArrivalsByPathIds'], params=[ids], endpoint_args=None)

    def Proxy(self, ) -> ResponseModel | ApiError:
        '''
        Forwards any remaining requests to the back-end

        ResponseModel.content contains `models.ObjectResponse` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)
