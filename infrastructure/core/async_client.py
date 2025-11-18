# Async Client Base Class
# This module provides the base class for generated async API clients.

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


import pkgutil
from datetime import UTC, datetime, timedelta
from email.utils import parsedate_to_datetime
from importlib import import_module
from typing import Any

from pydantic import BaseModel, RootModel

from pydantic_tfl_api import models

from .async_rest_client import AsyncRestClient
from .http_client import AsyncHTTPClientBase
from .package_models import ApiError, ResponseModel
from .response import UnifiedResponse


class AsyncClient:
    """Async base client for generated API clients.

    :param str api_token: API token to access TfL unified API
    :param AsyncHTTPClientBase http_client: Async HTTP client implementation (defaults to AsyncHttpxClient)
    """

    def __init__(self, api_token: str | None = None, http_client: AsyncHTTPClientBase | None = None):
        self.client = AsyncRestClient(api_token, http_client)
        self.models = self._load_models()

    def _load_models(self) -> dict[str, type[BaseModel]]:
        """Load all Pydantic models for deserialization."""
        models_dict: dict[str, type[BaseModel]] = {}

        # Load models from individual model files
        for _importer, modname, _ispkg in pkgutil.iter_modules(models.__path__):
            module = import_module(f"..models.{modname}", __package__)
            for model_name in dir(module):
                attr = getattr(module, model_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel):
                    models_dict[model_name] = attr

        # Also load models imported in the main models module (like GenericResponseModel)
        for model_name in dir(models):
            if not model_name.startswith("_"):  # Skip private attributes
                attr = getattr(models, model_name)
                if isinstance(attr, type) and issubclass(attr, BaseModel):
                    models_dict[model_name] = attr

        # Register core models used for error handling
        models_dict["ApiError"] = ApiError

        return models_dict

    @staticmethod
    def _parse_int_or_none(value: str) -> int | None:
        """Parse integer from string or return None."""
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_maxage_headers_from_cache_control_header(response: UnifiedResponse) -> tuple[int | None, int | None]:
        """Extract max-age values from Cache-Control header."""
        cache_control = response.headers.get("Cache-Control")
        if cache_control is None:
            return None, None
        directives = cache_control.split(", ")
        directive_dict = {d.split("=")[0]: d.split("=")[1] for d in directives if "=" in d}
        smaxage = AsyncClient._parse_int_or_none(directive_dict.get("s-maxage", ""))
        maxage = AsyncClient._parse_int_or_none(directive_dict.get("max-age", ""))
        return smaxage, maxage

    @staticmethod
    def _parse_timedelta(value: int | None, base_time: datetime | None) -> datetime | None:
        """Calculate datetime from timedelta and base time."""
        try:
            return base_time + timedelta(seconds=value) if value is not None and base_time is not None else None
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _get_result_expiry(response: UnifiedResponse) -> tuple[datetime | None, datetime | None]:
        """Calculate expiry times from response headers."""
        s_maxage, maxage = AsyncClient._get_maxage_headers_from_cache_control_header(response)
        date_header = response.headers.get("Date")
        request_datetime = parsedate_to_datetime(date_header) if date_header else None

        s_maxage_expiry = AsyncClient._parse_timedelta(s_maxage, request_datetime)
        maxage_expiry = AsyncClient._parse_timedelta(maxage, request_datetime)

        return s_maxage_expiry, maxage_expiry

    @staticmethod
    def _get_datetime_from_response_headers(response: UnifiedResponse) -> datetime | None:
        """Extract datetime from response Date header."""
        response_headers = response.headers
        try:
            date_header = response_headers.get("Date")
            return parsedate_to_datetime(date_header) if date_header else None
        except (TypeError, ValueError):
            return None

    def _deserialize(self, model_name: str, response: UnifiedResponse) -> Any:
        """Deserialize response into a model instance."""
        shared_expiry, result_expiry = self._get_result_expiry(response)
        response_date_time = self._get_datetime_from_response_headers(response)
        Model = self._get_model(model_name)
        data = response.json()

        result = self._create_model_instance(Model, data, result_expiry, shared_expiry, response_date_time)

        return result

    def _get_model(self, model_name: str) -> type[BaseModel]:
        """Get model class by name."""
        Model = self.models.get(model_name)
        if Model is None:
            raise ValueError(f"No model found with name {model_name}")
        return Model

    def _create_model_instance(
        self,
        model: BaseModel,
        response_json: Any,
        result_expiry: datetime | None,
        shared_expiry: datetime | None,
        response_date_time: datetime | None,
    ) -> ResponseModel:
        """Create a ResponseModel instance containing the deserialized content."""
        is_root_model = isinstance(model, type) and issubclass(model, RootModel)

        # Adjust for root models: RootModel expects one positional argument
        if is_root_model:
            if not isinstance(response_json, (list)):
                response_json = [response_json]
            content = model(response_json)
        else:
            content = model(**response_json) if isinstance(response_json, dict) else model(response_json)

        return ResponseModel(
            content_expires=result_expiry,
            shared_expires=shared_expiry,
            content=content,
            response_timestamp=response_date_time,
        )

    def _deserialize_error(self, response: UnifiedResponse) -> ApiError:
        """Deserialize error response into ApiError model."""
        # if content is json, deserialize it, otherwise manually create an ApiError object
        if response.headers.get("Content-Type") == "application/json":
            result = self._deserialize("ApiError", response)
            return result.content  # Extract ApiError from ResponseModel
        # Get timestamp from Date header, or use current time if not present
        date_header = response.headers.get("Date")
        timestamp = parsedate_to_datetime(date_header) if date_header else datetime.now(UTC)
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)
        return ApiError(
            timestamp_utc=timestamp,
            exception_type="Unknown",
            http_status_code=response.status_code,
            http_status=response.reason,
            relative_uri=response.url,
            message=response.text,
        )

    async def _send_request_and_deserialize(
        self,
        base_url: str,
        endpoint_and_model: dict[str, str],
        params: str | float | list[str | int | float] | None = None,
        endpoint_args: dict[str, Any] | None = None,
    ) -> ResponseModel | ApiError:
        """Send async request and deserialize the response.

        Args:
            base_url: The base URL for the API.
            endpoint_and_model: Dict containing 'uri' and 'model' keys.
            params: Optional path parameters.
            endpoint_args: Optional query parameters.

        Returns:
            ResponseModel on success or ApiError on failure.
        """
        if params is None:
            params = []
        if not isinstance(params, list):
            params = [params]

        endpoint = endpoint_and_model["uri"].format(*params)
        model_name = endpoint_and_model["model"]

        response = await self.client.send_request(base_url, endpoint, endpoint_args)

        if response.status_code != 200:
            return self._deserialize_error(response)
        return self._deserialize(model_name, response)
