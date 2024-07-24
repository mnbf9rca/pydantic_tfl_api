# portions of this code are from https://github.com/dhilmathy/TfL-python-api
# MIT License

# Copyright (c) 2018 Mathivanan Palanisamy
# Copyright (c) 2024 Rob Aleck

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from .config import endpoints
from .rest_client import RestClient
from importlib import import_module
from typing import Any, Literal, List, Optional, Tuple
from requests import Response
import pkgutil
from pydantic import BaseModel
from . import models
from datetime import datetime, timedelta
from email.utils import parsedate_to_datetime


class Client:
    """Client

    :param str api_token: API token to access TfL unified API
    """

    def __init__(self, api_token: str = None):
        self.client = RestClient(api_token)
        self.models = self._load_models()

    def _load_models(self):
        models_dict = {}
        for importer, modname, ispkg in pkgutil.iter_modules(models.__path__):
            module = import_module(f".models.{modname}", __package__)
            for model_name in dir(module):
                attr = getattr(module, model_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel):
                    models_dict[model_name] = attr
        # print(models_dict)
        return models_dict

    @staticmethod
    def _parse_int_or_none(value: str) -> int | None:
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_maxage_headers_from_cache_control_header(response: Response) -> Tuple[Optional[int], Optional[int]]:
        cache_control = response.headers.get("Cache-Control")
        # e.g. 'public, must-revalidate, max-age=43200, s-maxage=86400'
        if cache_control is None:
            return None, None
        directives = cache_control.split(", ")
        # e.g. ['public', 'must-revalidate', 'max-age=43200', 's-maxage=86400']
        directives = {d.split("=")[0]: d.split("=")[1]
                      for d in directives if "=" in d}
        smaxage = Client._parse_int_or_none(directives.get("s-maxage", ""))
        maxage = Client._parse_int_or_none(directives.get("max-age", ""))
        return smaxage, maxage

    @staticmethod
    def _parse_timedelta(value: Optional[int], base_time: Optional[datetime]) -> Optional[datetime]:
        try:
            return base_time + timedelta(seconds=value) if value is not None and base_time is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_result_expiry(response: Response) -> Tuple[datetime | None, datetime | None]:
        s_maxage, maxage = Client._get_maxage_headers_from_cache_control_header(
            response)
        request_datetime = parsedate_to_datetime(response.headers.get(
            "Date")) if "Date" in response.headers else None

        s_maxage_expiry = Client._parse_timedelta(s_maxage, request_datetime)
        maxage_expiry = Client._parse_timedelta(maxage, request_datetime)

        return s_maxage_expiry, maxage_expiry

    def _deserialize(self, model_name: str, response: Response) -> Any:
        shared_expiry, result_expiry = self._get_result_expiry(response)
        Model = self._get_model(model_name)
        data = response.json()

        result = self._create_model_instance(
            Model, data, result_expiry, shared_expiry)

        return result

    def _get_model(self, model_name: str) -> BaseModel:
        Model = self.models.get(model_name)
        if Model is None:
            raise ValueError(f"No model found with name {model_name}")
        return Model

    def _create_model_instance(
        self, Model: BaseModel,
        response_json: Any,
        result_expiry: datetime | None,
        shared_expiry: datetime | None
    ) -> BaseModel | List[BaseModel]:
        if isinstance(response_json, dict):
            return self._create_model_with_expiry(Model, response_json, result_expiry, shared_expiry)
        else:
            return [
                self._create_model_with_expiry(
                    Model, item, result_expiry, shared_expiry)
                for item in response_json
            ]

    def _create_model_with_expiry(
        self, Model: BaseModel, response_json: Any, result_expiry: Optional[datetime], shared_expiry: Optional[datetime]
    ):
        instance = Model(**response_json)
        instance.content_expires = result_expiry
        instance.shared_expires = shared_expiry
        return instance

    def _deserialize_error(self, response: Response) -> models.ApiError:
        # if content is json, deserialize it, otherwise manually create an ApiError object
        if response.headers.get("Content-Type") == "application/json":
            return self._deserialize("ApiError", response)
        return models.ApiError(
            timestampUtc=parsedate_to_datetime(response.headers.get("Date")),
            exceptionType="Unknown",
            httpStatusCode=response.status_code,
            httpStatus=response.reason,
            relativeUri=response.url,
            message=response.text,
        )

    def _send_request_and_deserialize(
        self, endpoint_and_model: dict[str, str],
        params: str | int | List[str | int] = None, endpoint_args: dict = None
    ) -> BaseModel | List[BaseModel] | models.ApiError:
        if params is None:
            params = []
        if not isinstance(params, list):
            params = [params]

        endpoint = endpoint_and_model["uri"].format(*params)
        model_name = endpoint_and_model["model"]

        response = self.client.send_request(endpoint, endpoint_args)

        if response.status_code != 200:
            return self._deserialize_error(response)
        return self._deserialize(model_name, response)

    def get_stop_points_by_line_id(
        self, line_id: str
    ) -> models.StopPoint | List[models.StopPoint] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointsByLineId"], line_id)

    def get_line_meta_modes(self) -> List[models.Mode] | models.ApiError:
        """
        Gets a list of valid modes.

        TfL API operation: Line_MetaModes

        Returns:
            List[models.Mode] | models.ApiError: A list of modes or an error.
        """
        return self._send_request_and_deserialize(endpoints["Line_MetaModes"])

    def get_lines_by_id(
        self, line_id: str 
    ) -> List[models.Line] | models.ApiError:
        """
        Gets lines that match the specified line ids.

        TfL API operation: Line_GetByPathIds

        Args:
            line_id (str): A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.

        Returns:
            List[models.Line] | models.ApiError: The line status or an error.
        """
        return self._send_request_and_deserialize(endpoints["Line_GetByPathIds"], line_id)

    def get_lines_by_mode(
        self, modes: str
    ) -> models.Line | List[models.Line] | models.ApiError:
        """
        Gets lines that serve the given modes.

        TfL API operation: Line_GetByModeByPathModes

        Args:
            modes (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
        
        Returns:
            List[models.Line] | models.ApiError: The line status or an error.
        """
        return self._send_request_and_deserialize(endpoints["Line_GetByModeByPathModes"], modes)


    def get_line_status(
        self, line_ids: str, include_details: bool = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        """
        Gets the line status of for given line ids e.g Minor Delays.

        TfL API operation: Line_StatusByIdsByPathIdsQueryDetail

        Args:
            line_ids (str): A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.
            include_details (bool, optional): Include details of the disruptions that are causing the line status, including the affected stops and routes. Default is None.

        Returns:
            List[models.Line] | models.ApiError: The line status or an error.
        """
        return self._send_request_and_deserialize(
            endpoints["Line_StatusByIdsByPathIdsQueryDetail"], line_ids, {"detail": include_details}
        )

    def get_line_status_severity(
        self, severity: str
    ) -> List[models.Line] | models.ApiError:
        """
        Gets the line status for all lines with a given severity A list of valid severity codes can be obtained from a call to Line/Meta/Severity.

        TfL API operation: Line_StatusBySeverityByPathSeverity

        Args:
            severity (int): Format - int32. The level of severity (eg: a number from 0 to 14)

        Returns:
            List[models.Line] | models.ApiError: The line status or an error.
        """
        return self._send_request_and_deserialize(
            endpoints["Line_StatusBySeverityByPathSeverity"], severity
        )

    def get_line_status_by_mode(
        self, mode: str, detail: bool = False, severity_level: int = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        """
        Get the line status for all lines for the given modes.

        TfL API operation: Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel

        Args:
            mode (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
            detail (bool): Include details of the disruptions that are causing the line status, including the affected stops and routes. Default is False.
            severity_level (int, optional): If specified, ensures that only those line status(es) are returned within the lines that have disruptions with the matching severity level. Default is None.

        Returns:
            models.Line | List[models.Line] | models.ApiError: The line status or an error.
        """
        endpoint_args =  {"detail": detail}
        if severity_level is not None:
            endpoint_args["severity"] = severity_level
        return self._send_request_and_deserialize(
            endpoints["Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel"], mode, endpoint_args
        )

    def get_route_by_line_id(
        self, line_ids: str,
        service_types: Optional[List[Literal["regular", "night"]]] = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        """
        Get all valid routes for given line ids, including the name and id of the originating and terminating stops for each route.

        TfL API operation: Line_LineRoutesByIdsByPathIdsQueryServiceTypes

        Args:
            mode (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
            service_types (List[Literal["regular", "night"]], optional): A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.

        Returns:
            List[models.Line] | models.ApiError: The line disruptions or an error.

        """
        return self._send_request_and_deserialize(
            endpoints["Line_LineRoutesByIdsByPathIdsQueryServiceTypes"], line_ids, {"serviceTypes": service_types}
        )

    def get_route_by_mode(
        self, mode: str, service_types: Optional[List[Literal["regular", "night"]]] = None
    ) -> List[models.Line] | models.ApiError:
        """
        Gets all lines and their valid routes for given modes, including the name and id of the originating and terminating stops for each route.

        TfL API operation: Line_DisruptionByPathIds

        Args:
            mode (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
            service_types (List[Literal["regular", "night"]], optional): A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.

        Returns:
            List[models.Line] | models.ApiError: The line disruptions or an error.

        """
        return self._send_request_and_deserialize(
            endpoints["Line_RouteByModeByPathModesQueryServiceTypes"], mode, {"serviceTypes": service_types}
        )

    def get_route_by_line_id_with_direction(
        self, line_id: str, direction: Literal["inbound", "outbound", "all"],
        service_types: Optional[List[Literal["regular", "night"]]] = None,
        exclude_crowding: Optional[bool] = None
    ) -> models.RouteSequence | List[models.RouteSequence] | models.ApiError:
        """
        Gets all valid routes for given line id, including the sequence of stops on each route.

        TfL API operation: Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding

        Args:
            line_id (str): A single line id e.g. victoria
            direction: The direction of travel. Can be inbound or outbound [or all].
            service_types (List[Literal["regular", "night"]], optional): A comma seperated list of service types to filter on. Supported values: Regular, Night. Defaulted to 'Regular' if not specified.
            exclude_crowding (bool, optional): That excludes crowding from line disruptions. Can be true or false.

        Returns:
            models.Disruption | List[models.Disruption] | models.ApiError: The line disruptions or an error.

        """
        # TODO test this works
        endpoint_args = {"serviceTypes": service_types, "excludeCrowding": exclude_crowding}
        return self._send_request_and_deserialize(
            endpoints["Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding"], [line_id, direction], endpoint_args
        )

    def get_line_disruptions_by_line_id(
        self, line_id: str
    ) -> models.Disruption | List[models.Disruption] | models.ApiError:
        """
        Get disruptions for the given line ids.

        TfL API operation: Line_DisruptionByPathIds

        Args:
            line_id (str): A comma-separated list of line ids e.g. victoria,circle,N133. Max. approx. 20 ids.

        Returns:
            models.Disruption | List[models.Disruption] | models.ApiError: The line disruptions or an error.

        """
        return self._send_request_and_deserialize(
            endpoints["Line_DisruptionByPathIds"], line_id
        )

    def get_line_disruptions_by_mode(
        self, mode: str
    ) -> models.Disruption | List[models.Disruption] | models.ApiError:
        """
        Get disruptions for all lines of the given modes.

        TfL API operation: Line_DisruptionByModeByPathModes

        Args:
            mode (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
    
        Returns:
            models.Disruption | List[models.Disruption] | models.ApiError: The line disruptions or an error.
        """
        return self._send_request_and_deserialize(
            endpoints["Line_DisruptionByModeByPathModes"], mode
        )

    def get_stop_points_by_id(
        self, id: str
    ) -> models.StopPoint | List[models.StopPoint] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointById"], id
        )

    def get_stop_points_by_mode(
        self, mode: str
    ) -> models.StopPointsResponse | List[models.StopPointsResponse] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointByMode"], mode
        )

    def get_stop_point_meta_modes(
        self,
    ) -> models.Mode | List[models.Mode] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointMetaModes"]
        )

    def get_arrivals_by_line_id(
        self, line_id: str
    ) -> models.Prediction | List[models.Prediction] | models.ApiError:
        """
        Get the list of arrival predictions for given line ids based at the given stop.

        TfL API operation: Line_ArrivalsByPathIds

        Args:
            mode (str): A comma-separated list of modes to filter by. e.g., 'tube,dlr'
    
        Returns:
            models.Prediction | List[models.Prediction] | models.ApiError: A list of predictions.
        """
        return self._send_request_and_deserialize(
            endpoints["Line_ArrivalsByPathIds"], line_id
        )
