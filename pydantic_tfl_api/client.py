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
from typing import Any, Literal, List, Optional
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

    def _get_s_maxage_from_cache_control_header(self, response: Response) -> int | None:
        cache_control = response.headers.get("cache-control")
        # e.g. 'public, must-revalidate, max-age=43200, s-maxage=86400'
        if cache_control is None:
            return None
        directives = cache_control.split(" ")
        # e.g. ['public,', 'must-revalidate,', 'max-age=43200,', 's-maxage=86400']
        directives = {d.split("=")[0]: d.split("=")[1] for d in directives if "=" in d}
        return None if "s-maxage" not in directives else int(directives["s-maxage"])

    def _get_result_expiry(self, response: Response) -> datetime | None:
        s_maxage = self._get_s_maxage_from_cache_control_header(response)
        request_datetime = parsedate_to_datetime(response.headers.get("date")) if "date" in response.headers else None
        if s_maxage and request_datetime:
            return request_datetime + timedelta(seconds=s_maxage)
        return None

    def _deserialize(self, model_name: str, response: Response) -> Any:
        result_expiry = self._get_result_expiry(response)
        Model = self._get_model(model_name)
        data = response.json()

        result = self._create_model_instance(Model, data, result_expiry)

        return result

    def _get_model(self, model_name: str) -> BaseModel:
        Model = self.models.get(model_name)
        if Model is None:
            raise ValueError(f"No model found with name {model_name}")
        return Model

    def _create_model_instance(
        self, Model: BaseModel, response_json: Any, result_expiry: datetime | None
    ) -> BaseModel | List[BaseModel]:
        if isinstance(response_json, dict):
            return self._create_model_with_expiry(Model, response_json, result_expiry)
        else:
            return [
                self._create_model_with_expiry(Model, item, result_expiry)
                for item in response_json
            ]

    def _create_model_with_expiry(
        self, Model: BaseModel, response_json: Any, result_expiry: datetime | None
    ):
        instance = Model(**response_json)
        instance.content_expires = result_expiry
        return instance

    def _deserialize_error(self, response: Response) -> models.ApiError:
        # if content is json, deserialize it, otherwise manually create an ApiError object
        if response.headers.get("content-type") == "application/json":
            return self._deserialize("ApiError", response)
        return models.ApiError(
            timestampUtc=parsedate_to_datetime(response.headers.get("date")),
            exceptionType="Unknown",
            httpStatusCode=response.status_code,
            httpStatus=response.reason,
            relativeUri=response.url,
            message=response.text,
        )

    def _send_request_and_deserialize(
        self, endpoint: str, model_name: str, endpoint_args: dict = None
    ) -> BaseModel | List[BaseModel] | models.ApiError:
        response = self.client.send_request(endpoint, endpoint_args)
        if response.status_code != 200:
            return self._deserialize_error(response)
        return self._deserialize(model_name, response)

    def get_stop_points_by_line_id(
        self, line_id: str
    ) -> models.StopPoint | List[models.StopPoint] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointsByLineId"].format(line_id), "StopPoint"
        )

    def get_line_meta_modes(self) -> models.Mode | models.ApiError:
        return self._send_request_and_deserialize(endpoints["lineMetaModes"], "Mode")

    def get_lines(
        self, line_id: str | None = None, mode: str | None = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        if line_id is None and mode is None:
            raise ValueError(
                "Either the --line_id argument or the --mode argument needs to be specified."
            )
        if line_id is not None:
            endpoint = endpoints["linesByLineId"].format(line_id)
        else:
            endpoint = endpoints["linesByMode"].format(mode)
        return self._send_request_and_deserialize(endpoint, "Line")

    def get_line_status(
        self, line: str, include_details: bool = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["lineStatus"].format(line), "Line", {"detail": include_details}
        )

    def get_line_status_severity(
        self, severity: str
    ) -> models.Line | List[models.Line] | models.ApiError:
        """
        severity: The level of severity (eg: a number from 0 to 14)
        """
        return self._send_request_and_deserialize(
            endpoints["lineStatusBySeverity"].format(severity), "Line"
        )

    def get_line_status_by_mode(
        self, mode: str
    ) -> models.Line | List[models.Line] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["lineStatusByMode"].format(mode), "Line"
        )

    def get_route_by_line_id(
        self, line_id: str
    ) -> models.Line | List[models.Line] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["routeByLineId"].format(line_id), "Line"
        )

    def get_route_by_mode(
        self, mode: str, service_types: Optional[List[Literal["regular", "night"]]] = None
    ) -> models.Line | List[models.Line] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["routeByMode"].format(mode), "Line", {"serviceTypes": service_types}
        )

    def get_route_by_line_id_with_direction(
        self, line_id: str, direction: Literal["inbound", "outbound", "all"]
    ) -> models.RouteSequence | List[models.RouteSequence] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["routeByLineIdWithDirection"].format(line_id, direction),
            "RouteSequence",
        )

    def get_line_disruptions_by_line_id(
        self, line_id: str
    ) -> models.Disruption | List[models.Disruption] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["lineDisruptionsByLineId"].format(line_id), "Disruption"
        )

    def get_line_disruptions_by_mode(
        self, mode: str
    ) -> models.Disruption | List[models.Disruption] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["lineDisruptionsByMode"].format(mode), "Disruption"
        )

    def get_stop_points_by_id(
        self, id: str
    ) -> models.StopPoint | List[models.StopPoint] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointById"].format(id), "StopPoint"
        )

    def get_stop_points_by_mode(
        self, mode: str
    ) -> models.StopPointsResponse | List[models.StopPointsResponse] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointByMode"].format(mode), "StopPointsResponse"
        )

    def get_stop_point_meta_modes(
        self,
    ) -> models.Mode | List[models.Mode] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["stopPointMetaModes"], "Mode"
        )

    def get_arrivals_by_line_id(
        self, line_id: str
    ) -> models.Prediction | List[models.Prediction] | models.ApiError:
        return self._send_request_and_deserialize(
            endpoints["arrivalsByLineId"].format(line_id), "Prediction"
        )
