import json
from datetime import UTC, datetime, timedelta
from email.utils import format_datetime, parsedate_to_datetime
from typing import Any
from unittest.mock import Mock, patch

import pytest

# from importlib import import_module
# import pkgutil
from pydantic import BaseModel, ConfigDict, ValidationError

from pydantic_tfl_api import models
from pydantic_tfl_api.core import ApiError, Client, ResponseModel, RestClient
from pydantic_tfl_api.core.http_client import HTTPResponse


def create_mock_http_response(
    status_code: int = 200,
    headers: dict[str, str] | None = None,
    text: str = "",
    url: str = "http://test.com",
    reason: str = "OK",
    content: bytes | None = None,
) -> Mock:
    """Create a mock HTTPResponse protocol-compliant object.

    This helper creates Mock objects that conform to the HTTPResponse protocol,
    enabling tests to work with any HTTP backend.
    """
    mock = Mock(spec=HTTPResponse)
    mock.status_code = status_code
    mock.headers = headers or {}
    mock.text = text
    mock.url = url
    mock.reason = reason

    # Handle content for _content attribute compatibility
    if content is not None:
        mock._content = content

    # Handle json() method
    if text:
        try:
            mock.json.return_value = json.loads(text)
        except (json.JSONDecodeError, ValueError):
            mock.json.return_value = {}
    else:
        mock.json.return_value = {}

    return mock


# Mock models module
class MockModel(BaseModel):
    key: str


class PydanticTestModel(BaseModel):
    name: str
    age: int
    content_expires: datetime | None = None
    shared_expires: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


def test_create_client_with_api_token() -> None:
    # checks that the API key is being passed to the RestClient
    api_token = "your_app_key"
    test_client = Client(api_token)
    assert test_client.client.app_key is not None and test_client.client.app_key["app_key"] == api_token


@pytest.mark.parametrize(
    "Model, response_json, result_expiry, shared_expiry, expected_name, expected_age, expected_expiry, expected_shared_expiry",  # noqa: E501
    [
        # Happy path tests
        (
            PydanticTestModel,
            {"name": "Alice", "age": 30},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
            "Alice",
            30,
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
        ),
        (
            PydanticTestModel,
            {"name": "Bob", "age": 25},
            None,
            None,
            "Bob",
            25,
            None,
            None,
        ),
        # Edge cases
        (
            PydanticTestModel,
            {"name": "", "age": 0},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
            "",
            0,
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
        ),
        (
            PydanticTestModel,
            {"name": "Charlie", "age": -1},
            None,
            None,
            "Charlie",
            -1,
            None,
            None,
        ),
    ],
    ids=[
        "happy_path_with_expiry",
        "happy_path_without_expiry",
        "edge_case_empty_name_and_zero_age",
        "edge_case_negative_age",
    ],
)
def test_create_model_instance(
    Model: type[BaseModel],
    response_json: dict[str, Any],
    result_expiry: datetime | None,
    shared_expiry: datetime | None,
    expected_name: str,
    expected_age: int,
    expected_expiry: datetime | None,
    expected_shared_expiry: datetime | None,
) -> None:
    # Act
    client = Client()
    response_json_parsed = json.loads(json.dumps(response_json))
    response_date_time = datetime(2023, 12, 31, 1, 2, 3, tzinfo=UTC)

    # Create model instance
    instance = client._create_model_instance(
        Model, response_json_parsed, result_expiry, shared_expiry, response_date_time
    )

    # Assertions
    assert isinstance(instance, ResponseModel)
    assert instance.content_expires == expected_expiry
    assert instance.shared_expires == expected_shared_expiry
    assert instance.response_timestamp == response_date_time
    instance_content = instance.content
    assert isinstance(instance_content, Model)
    assert isinstance(instance_content, PydanticTestModel)  # Type narrowing for mypy
    assert instance_content.name == expected_name
    assert instance_content.age == expected_age


# Error cases for model instance creation
@pytest.mark.parametrize(
    "Model, response_json, result_expiry, shared_expiry",
    [
        (
            PydanticTestModel,
            {"name": "Alice"},  # Missing age
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
        ),
        (
            PydanticTestModel,
            {"age": 30},  # Missing name
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
        ),
        (
            PydanticTestModel,
            {"name": "Alice", "age": "thirty"},  # Invalid age type
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
        ),
    ],
    ids=[
        "error_case_missing_age",
        "error_case_missing_name",
        "error_case_invalid_age_type",
    ],
)
def test_create_model_instance_validation_errors(
    Model: type[BaseModel],
    response_json: dict[str, Any],
    result_expiry: datetime | None,
    shared_expiry: datetime | None,
) -> None:
    # Act & Assert
    client = Client()
    response_json_parsed = json.loads(json.dumps(response_json))
    response_date_time = datetime(2023, 12, 31, 1, 2, 3, tzinfo=UTC)

    with pytest.raises(ValidationError):
        client._create_model_instance(Model, response_json_parsed, result_expiry, shared_expiry, response_date_time)


@pytest.mark.parametrize(
    "api_token, expected_client_type, expected_models",
    [
        (None, RestClient, {"test_model"}),
        ("valid_key", RestClient, {"test_model"}),
    ],
    ids=["no_api_token", "valid_api_token"],
)
def test_client_initialization(api_token: str | None, expected_client_type: type, expected_models: set[str]) -> None:
    # Arrange
    with (
        patch("pydantic_tfl_api.core.client.RestClient") as MockRestClient,
        patch(
            # f"{test_target}.client.Client._load_models", return_value=expected_models
            "pydantic_tfl_api.core.client.Client._load_models",
            return_value=expected_models,
        ) as MockLoadModels,
    ):
        MockRestClient.return_value = Mock(spec=RestClient)

        # Act
        test_client = Client(api_token)

        # Assert
        assert isinstance(test_client.client, expected_client_type)
        assert test_client.models == expected_models
        # RestClient now accepts optional http_client parameter (defaults to None)
        MockRestClient.assert_called_once_with(api_token, None)
        MockLoadModels.assert_called_once()


@pytest.mark.parametrize(
    "model_name, expected_type",
    [
        ("Line", BaseModel),
        ("StopPoint", BaseModel),
        ("Place", BaseModel),
        ("Mode", BaseModel),
        ("Prediction", BaseModel),
        ("GenericResponseModel", BaseModel),
    ],
    ids=["line_model", "stop_point_model", "place_model", "mode_model", "prediction_model", "generic_response_model"],
)
def test_load_models_contains_expected_models(model_name: str, expected_type: type[BaseModel]) -> None:
    """Test that Client loads expected real models and they are proper BaseModel subclasses."""
    # Act
    test_client = Client()

    # Assert
    assert model_name in test_client.models, f"Expected model {model_name} not found in loaded models"
    model_class = test_client.models[model_name]
    assert isinstance(model_class, type), f"Model {model_name} should be a class"
    assert issubclass(model_class, expected_type), f"Model {model_name} should be a BaseModel subclass"


def test_load_models_returns_non_empty_dict() -> None:
    """Test that _load_models returns a non-empty dictionary of models."""
    # Act
    test_client = Client()
    result = test_client.models

    # Assert
    assert isinstance(result, dict), "Models should be returned as a dictionary"
    assert len(result) > 10, f"Expected many models to be loaded, got {len(result)}"

    # Verify all values are BaseModel subclasses
    for model_name, model_class in result.items():
        assert isinstance(model_class, type), f"Model {model_name} should be a class"
        assert issubclass(model_class, BaseModel), f"Model {model_name} should be a BaseModel subclass"


@pytest.mark.parametrize(
    "cache_control_header, expected_result",
    [
        # s-maxage present and valid
        (
            "public, must-revalidate, max-age=43200, s-maxage=86400",
            (86400, 43200),
        ),
        # s-maxage absent, only max-age present
        (
            "public, must-revalidate, max-age=43200",
            (None, 43200),
        ),
        # No cache-control header
        (
            None,
            (None, None),
        ),
        # Negative s-maxage value
        (
            "public, must-revalidate, max-age=43200, s-maxage=-1",
            (-1, 43200),
        ),
        # No max-age or s-maxage present
        (
            "public, must-revalidate",
            (None, None),
        ),
        # Only s-maxage present
        (
            "public, s-maxage=86400",
            (86400, None),
        ),
        # Both max-age and s-maxage zero
        (
            "public, max-age=0, s-maxage=0",
            (0, 0),
        ),
        # Malformed max-age directive
        (
            "public, must-revalidate, max-age=foo, s-maxage=86400",
            (86400, None),
        ),
        # Malformed s-maxage directive
        (
            "public, must-revalidate, max-age=43200, s-maxage=bar",
            (None, 43200),
        ),
        # Only s-maxage without a value
        (
            "public, must-revalidate, s-maxage=",
            (None, None),
        ),
        # Only max-age without a value
        (
            "public, must-revalidate, max-age=",
            (None, None),
        ),
        # max-age and s-maxage with additional spaces
        (
            "public, max-age= 3600 , s-maxage= 7200 ",
            (7200, 3600),
        ),
        # Complex header with multiple spaces and ordering
        (
            "must-revalidate, public, s-maxage=7200, max-age=3600",
            (7200, 3600),
        ),
    ],
    ids=[
        "s-maxage_present",
        "s-maxage_absent",
        "no_cache_control_header",
        "negative_s-maxage_value",
        "no_max-age_or_s-maxage",
        "only_s-maxage_present",
        "both_max-age_and_s-maxage_zero",
        "malformed_max-age",
        "malformed_s-maxage",
        "s-maxage_no_value",
        "max-age_no_value",
        "max-age_and_s-maxage_with_spaces",
        "complex_header",
    ],
)
def test_get_maxage_headers_from_cache_control_header(
    cache_control_header: str | None, expected_result: tuple[int | None, int | None]
) -> None:
    # Create mock response with headers
    headers = {"Cache-Control": cache_control_header} if cache_control_header else {}
    response = create_mock_http_response(headers=headers)

    # Act
    result = Client._get_maxage_headers_from_cache_control_header(response)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "model_name, response_content, expected_result",
    [
        (
            "MockModel",
            {"key": "value"},
            MockModel(key="value"),
        ),
        (
            "MockModel",
            [{"key": "value"}, {"key": "value2"}],
            [MockModel(key="value"), MockModel(key="value2")],
        ),
    ],
    ids=[
        "single_model",
        "list_of_models",
    ],
)
def test_deserialize(
    model_name: str,
    response_content: dict[str, str] | list[dict[str, str]],
    expected_result: MockModel | list[MockModel],
) -> None:
    # Create mock response
    response_date_time = datetime(2023, 12, 31, 1, 2, 3, tzinfo=UTC)
    response_date_time_string = format_datetime(response_date_time)
    Response_Object = create_mock_http_response(
        headers={"Date": response_date_time_string}, text=json.dumps(response_content)
    )
    Response_Object.json.return_value = response_content

    # Act

    test_client = Client()
    return_datetime = datetime(2024, 7, 12, 13, 00, 00)
    return_datetime_2 = datetime(2025, 7, 12, 13, 00, 00)

    with (
        patch.object(
            test_client,
            "_get_result_expiry",
            return_value=(return_datetime_2, return_datetime),
        ),
        patch.object(test_client, "_get_model", return_value=MockModel) as mock_get_model,
        patch.object(test_client, "_create_model_instance", return_value=expected_result) as mock_create_model_instance,
    ):
        result = test_client._deserialize(model_name, Response_Object)

    # Assert
    assert result == expected_result
    mock_get_model.assert_called_with(model_name)
    mock_create_model_instance.assert_called_with(
        MockModel, Response_Object.json.return_value, return_datetime, return_datetime_2, response_date_time
    )


@pytest.mark.parametrize(
    "value, base_time, expected_result",
    [
        # Valid timedelta
        (
            86400,
            datetime(2023, 11, 15, 12, 45, 26),
            datetime(2023, 11, 16, 12, 45, 26),
        ),
        # None value for timedelta
        (
            None,
            datetime(2023, 11, 15, 12, 45, 26),
            None,
        ),
        # None value for base_time
        (
            86400,
            None,
            None,
        ),
        # Both value and base_time are None
        (
            None,
            None,
            None,
        ),
        # Edge case: zero timedelta
        (
            0,
            datetime(2023, 11, 15, 12, 45, 26),
            datetime(2023, 11, 15, 12, 45, 26),
        ),
        # Negative timedelta
        (
            -86400,
            datetime(2023, 11, 15, 12, 45, 26),
            datetime(2023, 11, 14, 12, 45, 26),
        ),
    ],
    ids=[
        "valid_timedelta",
        "none_value",
        "none_base_time",
        "both_none",
        "zero_timedelta",
        "negative_timedelta",
    ],
)
def test_parse_timedelta(value: int, base_time: datetime, expected_result: datetime) -> None:
    # Act
    result = Client._parse_timedelta(value, base_time)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "s_maxage, maxage, date_header, expected_result",
    [
        (
            86400,
            43200,
            {"Date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=86400),
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=43200),
            ),
        ),
        (
            None,
            43200,
            {"Date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                None,
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=43200),
            ),
        ),
        (
            86400,
            None,
            {"Date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=86400),
                None,
            ),
        ),
        (
            None,
            None,
            {"Date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (None, None),
        ),
        (
            86400,
            43200,
            {},
            (None, None),
        ),
        (
            None,
            43200,
            {},
            (None, None),
        ),
        (
            86400,
            None,
            {},
            (None, None),
        ),
        (
            None,
            None,
            {},
            (None, None),
        ),
    ],
    ids=[
        "s_maxage_and_date_present",
        "s_maxage_absent",
        "date_absent",
        "s_maxage_and_date_absent",
        "both_present_no_date",
        "maxage_present_no_date",
        "smaxage_present_no_date",
        "neither_present_no_date",
    ],
)
def test_get_result_expiry(
    s_maxage: int | None,
    maxage: int | None,
    date_header: dict[str, str],
    expected_result: tuple[datetime | None, datetime | None],
) -> None:
    # Create mock response with headers
    response = create_mock_http_response(headers=date_header)

    # Act
    with (
        patch(
            "pydantic_tfl_api.core.client.Client._get_maxage_headers_from_cache_control_header",
            return_value=(s_maxage, maxage),
        ),
        patch(
            "pydantic_tfl_api.core.client.Client._parse_timedelta",
            side_effect=[expected_result[0], expected_result[1]],
        ),
    ):
        result = Client._get_result_expiry(response)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "model_name, models_dict, expected_result",
    [
        (
            "MockModel",
            {"MockModel": MockModel},
            MockModel,
        ),
    ],
    ids=[
        "model_exists",
    ],
)
def test_get_model(model_name: str, models_dict: dict[str, type[BaseModel]], expected_result: type[BaseModel]) -> None:
    # Create a simple Client object
    test_client = Client()
    test_client.models = models_dict

    # Act
    result = test_client._get_model(model_name)

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "model_name, models_dict",
    [
        (
            "NonExistentModel",
            {"MockModel": MockModel},
        ),
    ],
    ids=[
        "model_does_not_exist",
    ],
)
def test_get_model_raises_error(model_name: str, models_dict: dict[str, type[BaseModel]]) -> None:
    # Create a simple Client object
    test_client = Client()
    test_client.models = models_dict

    # Act & Assert
    with pytest.raises(ValueError):
        test_client._get_model(model_name)


# @pytest.mark.parametrize(
#     "Model, response_json, result_expiry, shared_expiry, create_model_mock_return, expected_return",
#     [
#         (
#             MockModel,
#             {"name": "Alice", "age": 30},
#             datetime(2023, 12, 31),
#             datetime(2024, 12, 31),
#             "TestReturn1",
#             "TestReturn1",
#         ),
#         (
#             MockModel,
#             [{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 25}],
#             datetime(2023, 12, 31),
#             datetime(2024, 12, 31),
#             "TestReturn2",
#             "TestReturn2",
#         ),
#     ],
#     ids=[
#         "single_model",
#         "list_of_models",
#     ],
# )
# def test_create_model_instance_2(
#     Model, response_json, result_expiry, shared_expiry, create_model_mock_return, expected_return
# ):
#     # Mock Client
#     test_client = Client()

#     # Mock _create_model_instance
#     with patch.object(
#         test_client, "_create_model_instance", return_value=create_model_mock_return
#     ) as mock_create_model_instance:

#         # Act
#         result = test_client._create_model_instance(
#             Model, response_json, result_expiry, shared_expiry)

#         # Assert
#         assert result == expected_return
#         mock_create_model_instance.assert_called_with(
#             Model, response_json, result_expiry, shared_expiry
#         )


datetime_object_with_time_and_tz_utc = datetime(2023, 12, 31, 1, 2, 3, tzinfo=UTC)


@pytest.mark.parametrize(
    "content_type, response_content, expected_result",
    [
        (
            "application/json",
            {
                "timestampUtc": "Date",
                "exceptionType": "type",
                "httpStatusCode": 404,
                "httpStatus": "Not Found",
                "relativeUri": "/uri",
                "message": "message",
            },
            # _deserialize_error now returns raw text without JSON parsing
            ApiError(
                timestamp_utc=parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT"),
                exception_type="Not Found",
                http_status_code=404,
                http_status="Not Found",
                relative_uri="/uri",
                message='{"timestampUtc": "Date", "exceptionType": "type", "httpStatusCode": 404, "httpStatus": "Not Found", "relativeUri": "/uri", "message": "message"}',
            ),
        ),
        (
            "text/html",
            "Error message",
            ApiError(
                timestamp_utc=parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT"),
                exception_type="Not Found",
                http_status_code=404,
                http_status="Not Found",
                relative_uri="/uri",
                message='"Error message"',
            ),
        ),
    ],
    ids=[
        "json_content",
        "non_json_content",
    ],
)
def test_deserialize_error(
    content_type: str,
    response_content: dict[str, str | int] | str,
    expected_result: ApiError,
) -> None:
    # Create mock response
    content_text = json.dumps(response_content)
    response = create_mock_http_response(
        status_code=404,
        headers={
            "Content-Type": content_type,
            "Date": "Tue, 15 Nov 1994 12:45:26 GMT",
        },
        text=content_text,
        url="/uri",
        reason="Not Found",
    )
    # Set _content for compatibility with code that reads it directly
    response._content = bytes(content_text, "utf-8")

    test_client = Client()
    # Act - no mocking needed, _deserialize_error no longer calls _deserialize
    result = test_client._deserialize_error(response)

    # Assert
    assert result == expected_result


class SampleClient(Client):
    def Line_test_endpoint(
        self, modes: str, detail: bool | None = None, severityLevel: str | None = None
    ) -> ResponseModel[Any] | ApiError:
        """
        A test query. Gets the line status of for all lines for the given modes

        Parameters:
        modes: str - A comma-separated list of modes to filter by. e.g. tube,dlr. Example: tube
        detail: bool - Include details of the disruptions that are causing the line status including the affected stops and routes. Example: None given
        severityLevel: str - If specified, ensures that only those line status(es) are returned within the lines that have disruptions with the matching severity level.. Example: None given
        """
        base_url = "https://api.tfl.gov.uk"
        endpoints = {
            "Line_test_endpoint": {
                "uri": "/Line/Mode/{0}/Status",
                "model": "GenericResponseModel",
            },
        }
        return self._send_request_and_deserialize(
            base_url,
            endpoints["Line_test_endpoint"],
            params=[modes],
            endpoint_args={"detail": detail, "severityLevel": severityLevel},
        )


class Test_TfL_connectivity:
    def test_get_line_status_by_mode_rejected_with_invalid_api_key(self) -> None:
        api_token = "your_app_key"
        test_client = SampleClient(api_token)
        assert test_client.client.app_key is not None and test_client.client.app_key["app_key"] == api_token
        # should get a 429 error inside an ApiError object
        result = test_client.Line_test_endpoint("overground,tube")
        assert isinstance(result, ApiError)
        assert result.http_status_code == 429
        assert result.http_status == "Invalid App Key"

    def test_get_line_status_by_mode(self) -> None:
        # this API doesnt need authentication so we can use it to test that the API is working
        test_client = SampleClient()
        # should get a list of Line objects
        result = test_client.Line_test_endpoint("overground,tube")
        assert isinstance(result, ResponseModel)
        response_content = result.content
        assert isinstance(response_content, models.GenericResponseModel)


@pytest.mark.parametrize(
    "headers, expected_result",
    [
        ({"Date": "Tue, 15 Nov 1994 12:45:26 GMT"}, parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT")),
        ({}, None),
        ({"Date": "Invalid Date"}, None),
    ],
    ids=["valid_date", "no_date", "invalid_date"],
)
def test_get_datetime_from_response_headers(headers: dict[str, str], expected_result: datetime | None) -> None:
    # Create mock response with headers
    response = create_mock_http_response(headers=headers)

    # Act
    result = Client._get_datetime_from_response_headers(response)

    # Assert
    assert result == expected_result


# Regression tests for issue #143: ApiError model registration
class TestApiErrorRegistration:
    """Tests to ensure ApiError is properly registered and can be deserialized."""

    def test_api_error_is_registered_in_models_dict(self) -> None:
        """Verify that ApiError is registered in the Client's models dictionary.

        This is a regression test for issue #143 where ApiError was not registered,
        causing ValueError when trying to deserialize JSON error responses.
        """
        test_client = Client()

        # ApiError should be in the models dictionary
        assert "ApiError" in test_client.models, "ApiError should be registered in models dictionary"
        assert test_client.models["ApiError"] == ApiError, "ApiError should map to the correct class"

    def test_get_model_returns_api_error(self) -> None:
        """Verify that _get_model can successfully look up ApiError."""
        test_client = Client()

        # Should not raise ValueError
        model = test_client._get_model("ApiError")

        assert model == ApiError, "Should return ApiError class"

    def test_deserialize_error_json_without_mocking(self) -> None:
        """Test actual JSON error deserialization without mocking _deserialize.

        After issue #158, _deserialize_error no longer parses JSON content.
        It returns the raw response text as the message.
        """
        # Create a mock JSON error response from TfL API
        error_json = {
            "timestampUtc": "Mon, 15 Jan 2024 12:00:00 GMT",
            "exceptionType": "ApiException",
            "httpStatusCode": 429,
            "httpStatus": "Invalid App Key",
            "relativeUri": "/Line/Meta/Modes",
            "message": "Rate limit exceeded",
        }
        error_text = json.dumps(error_json)
        response = create_mock_http_response(
            status_code=429,
            headers={
                "Content-Type": "application/json",
                "Date": "Mon, 15 Jan 2024 12:00:00 GMT",
            },
            text=error_text,
            url="https://api.tfl.gov.uk/Line/Meta/Modes",
            reason="Too Many Requests",
        )
        response._content = bytes(error_text, "utf-8")

        test_client = Client()

        # This should return an ApiError with raw text
        result = test_client._deserialize_error(response)

        # Verify the result is an ApiError with raw response text
        assert isinstance(result, ApiError), "Should return an ApiError"
        assert result.http_status_code == 429
        assert result.http_status == "Too Many Requests"  # Uses response.reason
        assert result.exception_type == "Too Many Requests"  # Uses response.reason
        assert result.message == error_text  # Raw JSON text

    def test_deserialize_error_non_json(self) -> None:
        """Test error deserialization for non-JSON responses (control test)."""
        response = create_mock_http_response(
            status_code=500,
            headers={
                "Content-Type": "text/html",
                "Date": "Mon, 15 Jan 2024 12:00:00 GMT",
            },
            text="Internal Server Error",
            url="https://api.tfl.gov.uk/Line/Meta/Modes",
            reason="Internal Server Error",
        )
        response._content = b"Internal Server Error"

        test_client = Client()

        # Non-JSON path should still work (this was already working)
        result = test_client._deserialize_error(response)

        assert isinstance(result, ApiError), "Should return ApiError directly for non-JSON"
        assert result.http_status_code == 500
        assert result.exception_type == "Internal Server Error"

    def test_send_request_and_deserialize_error_response(self) -> None:
        """Test full flow: API call returning JSON error response."""
        from pydantic_tfl_api.core.response import UnifiedResponse

        test_client = SampleClient()

        # Create JSON error response
        error_json = {
            "timestampUtc": "Mon, 15 Jan 2024 12:00:00 GMT",
            "exceptionType": "EntityNotFoundException",
            "httpStatusCode": 400,
            "httpStatus": "Bad Request",
            "relativeUri": "/Line/Mode/invalid/Status",
            "message": "Invalid mode 'invalid'",
        }
        error_text = json.dumps(error_json)

        # Create a mock that satisfies the HTTPResponse protocol
        mock_http_response = Mock()
        mock_http_response.status_code = 400
        mock_http_response.reason = "Bad Request"
        mock_http_response.url = "https://api.tfl.gov.uk/Line/Mode/invalid/Status"
        mock_http_response.text = error_text
        mock_http_response.headers = {
            "Content-Type": "application/json",
            "Date": "Mon, 15 Jan 2024 12:00:00 GMT",
            "Cache-Control": "public, max-age=300",
        }
        mock_http_response.json.return_value = error_json

        # Mock at the RestClient.send_request level to return UnifiedResponse
        mock_unified_response = UnifiedResponse(mock_http_response)

        with patch.object(test_client.client, "send_request", return_value=mock_unified_response):
            result = test_client.Line_test_endpoint("invalid")

        # Should return ApiError with raw text (no JSON parsing after issue #158)
        assert isinstance(result, ApiError), "Should return ApiError for JSON error"
        assert result.http_status_code == 400
        assert result.http_status == "Bad Request"
        assert result.exception_type == "Bad Request"
        assert result.message == error_text  # Raw JSON text
