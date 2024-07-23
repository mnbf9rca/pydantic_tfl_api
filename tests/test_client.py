import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from requests.models import Response
from email.utils import parsedate_to_datetime

# from importlib import import_module
# import pkgutil

from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta, timezone

from pydantic_tfl_api.client import Client
from pydantic_tfl_api.rest_client import RestClient
from pydantic_tfl_api.models.api_error import ApiError


# Mock models module
class MockModel(BaseModel):
    pass


class PydanticTestModel(BaseModel):
    name: str
    age: int
    content_expires: datetime | None = None
    shared_expires: datetime | None = None


@pytest.mark.parametrize(
    "Model, response_json, result_expiry, shared_expiry, expected_name, expected_age, expected_expiry, expected_shared_expiry",
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
        # Error cases
        (
            PydanticTestModel,
            {"name": "Alice"},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
            None,
            None,
            None,
            None,
        ),  # Missing age
        (
            PydanticTestModel,
            {"age": 30},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
            None,
            None,
            None,
            None,
        ),  # Missing name
        (
            PydanticTestModel,
            {"name": "Alice", "age": "thirty"},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31, 23, 59, 59),
            None,
            None,
            None,
            None,
        ),  # Invalid age type
    ],
    ids=[
        "happy_path_with_expiry",
        "happy_path_without_expiry",
        "edge_case_empty_name_and_zero_age",
        "edge_case_negative_age",
        "error_case_missing_age",
        "error_case_missing_name",
        "error_case_invalid_age_type",
    ],
)
def test_create_model_with_expiry(
    Model, response_json, result_expiry, shared_expiry, expected_name, expected_age, expected_expiry, expected_shared_expiry
):

    # Act
    if expected_name is None:
        with pytest.raises(ValidationError):
            Client._create_model_with_expiry(None, Model, response_json, result_expiry, shared_expiry)
    else:
        instance = Client._create_model_with_expiry(
            None, Model, response_json, result_expiry, shared_expiry
        )

        # Assert
        assert instance.name == expected_name
        assert instance.age == expected_age
        assert instance.content_expires == expected_expiry
        assert instance.shared_expires == expected_shared_expiry


@pytest.mark.parametrize(
    "api_token, expected_client_type, expected_models",
    [
        (None, RestClient, {"test_model"}),
        ( "valid_key", RestClient, {"test_model"}),
    ],
    ids=["no_api_token", "valid_api_token"],
)
def test_client_initialization(api_token, expected_client_type, expected_models):

    # Arrange
    with patch("pydantic_tfl_api.client.RestClient") as MockRestClient, patch(
        "pydantic_tfl_api.client.Client._load_models", return_value=expected_models
    ) as MockLoadModels:
        MockRestClient.return_value = Mock(spec=RestClient)

        # Act
        client = Client(api_token)

        # Assert
        assert isinstance(client.client, expected_client_type)
        assert client.models == expected_models
        MockRestClient.assert_called_once_with(api_token)
        MockLoadModels.assert_called_once()


@pytest.mark.parametrize(
    "models_dict, expected_result",
    [
        (
            {"MockModel": MockModel},
            {"MockModel": MockModel},
        ),
        (
            {"MockModel1": MockModel, "MockModel2": MockModel},
            {"MockModel1": MockModel, "MockModel2": MockModel},
        ),
        (
            {"NotAModel": object},
            {},
        ),
        (
            {},
            {},
        ),
    ],
    ids=["single_model", "multiple_models", "no_pydantic_model", "no_models"],
)
def test_load_models(models_dict, expected_result):
    # Mock import_module
    with patch("pydantic_tfl_api.client.import_module") as mock_import_module:
        mock_module = MagicMock()
        mock_module.__dict__.update(models_dict)
        mock_import_module.return_value = mock_module

        # Mock pkgutil.iter_modules
        with patch("pydantic_tfl_api.client.pkgutil.iter_modules") as mock_iter_modules:
            mock_iter_modules.return_value = [
                (None, name, None) for name in models_dict.keys()
            ]

            # Act
            from pydantic_tfl_api.client import Client

            client = Client()
            result = client._load_models()

            # Assert
            assert result == expected_result


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
def test_get_maxage_headers_from_cache_control_header(cache_control_header, expected_result):
    # Mock Response
    response = Response()
    if cache_control_header is not None:
        response.headers = {"cache-control": cache_control_header}
    else:
        response.headers = {}

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
def test_deserialize(model_name, response_content, expected_result):
    # Mock Response
    Response_Object = MagicMock(Response)
    Response_Object.json.return_value = response_content # json.dumps(response_content)

    # Act

    client = Client()
    return_datetime = datetime(2024, 7, 12, 13, 00, 00)
    return_datetime_2 = datetime(2025, 7, 12, 13, 00, 00)

    with patch.object(
        client, "_get_result_expiry", return_value=(return_datetime_2, return_datetime)
    ), patch.object(
        client, "_get_model", return_value=MockModel
    ) as mock_get_model, patch.object(
        client, "_create_model_instance", return_value=expected_result
    ) as mock_create_model_instance:

        result = client._deserialize(model_name, Response_Object)

    # Assert
    assert result == expected_result
    mock_get_model.assert_called_with(model_name)
    mock_create_model_instance.assert_called_with(
        MockModel, Response_Object.json.return_value, return_datetime, return_datetime_2
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
def test_parse_timedelta(value, base_time, expected_result):
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
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=86400),
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=43200)
            ),
        ),
        (
            None,
            43200,
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                None,
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=43200)
            ),
        ),
        (
            86400,
            None,
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            (
                parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT") + timedelta(seconds=86400),
                None
            ),
        ),
        (
            None,
            None,
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
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
def test_get_result_expiry(s_maxage, maxage, date_header, expected_result):
    # Mock Response
    response = Response()
    response.headers.update(date_header)

    # Act
    client = Client()

    # Act
    with patch('pydantic_tfl_api.client.Client._get_maxage_headers_from_cache_control_header', return_value=(s_maxage, maxage)), \
         patch('pydantic_tfl_api.client.Client._parse_timedelta', side_effect=[expected_result[0], expected_result[1]]):
        result = Client._get_result_expiry(response)

    # Assert
    assert result == expected_result

    # Assert
    assert result == expected_result


@pytest.mark.parametrize(
    "model_name, models_dict, expected_result, exception",
    [
        (
            "MockModel",
            {"MockModel": MockModel},
            MockModel,
            None,
        ),
        (
            "NonExistentModel",
            {"MockModel": MockModel},
            None,
            ValueError,
        ),
    ],
    ids=[
        "model_exists",
        "model_does_not_exist",
    ],
)
def test_get_model(model_name, models_dict, expected_result, exception):
    # Create a simple Client object
    class SimpleClient:
        def __init__(self, models_to_set):
            self.models = models_to_set

    client = SimpleClient(models_dict)

    # Act and Assert
    if exception:
        with pytest.raises(exception):
            Client._get_model(client, model_name)
    else:
        result = Client._get_model(client, model_name)
        assert result == expected_result


@pytest.mark.parametrize(
    "Model, response_json, result_expiry, shared_expiry, create_model_mock_return, expected_return",
    [
        (
            MockModel,
            {"name": "Alice", "age": 30},
            datetime(2023, 12, 31),
            datetime(2024, 12, 31),
            "TestReturn1",
            "TestReturn1",
        ),
        (
            MockModel,
            [{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 25}],
            datetime(2023, 12, 31),
            datetime(2024, 12, 31),
            "TestReturn2",
            ["TestReturn2", "TestReturn2"],
        ),
    ],
    ids=[
        "single_model",
        "list_of_models",
    ],
)
def test_create_model_instance(
    Model, response_json, result_expiry, shared_expiry, create_model_mock_return, expected_return
):
    # Mock Client
    client = Client()

    # Mock _create_model_with_expiry
    with patch.object(
        client, "_create_model_with_expiry", return_value=create_model_mock_return
    ) as mock_create_model_with_expiry:

        # Act
        result = client._create_model_instance(Model, response_json, result_expiry, shared_expiry)

        # Assert
        assert result == expected_return
        if isinstance(response_json, dict):
            mock_create_model_with_expiry.assert_called_with(
                Model, response_json, result_expiry, shared_expiry
            )
        else:
            for item in response_json:
                mock_create_model_with_expiry.assert_any_call(Model, item, result_expiry, shared_expiry)

datetime_object_with_time_and_tz_utc = datetime(2023, 12, 31, 1, 2, 3, tzinfo=timezone.utc)

@pytest.mark.parametrize(
    "content_type, response_content, expected_result",
    [
        (
            "application/json",
            {"timestampUtc": "date", "exceptionType": "type", "httpStatusCode": 404, "httpStatus": "Not Found", "relativeUri": "/uri", "message": "message"},
            "_deserialize return value",
        ),
        (
            "text/html",
            "Error message",
            ApiError(timestampUtc=parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT"), exceptionType="Unknown", httpStatusCode=404, httpStatus="Not Found", relativeUri="/uri", message='"Error message"'),
        ),
    ],
    ids=[
        "json_content",
        "non_json_content",
    ]
)
def test_deserialize_error(content_type, response_content, expected_result):
    # Mock Response
    response = Response()
    response._content = bytes(json.dumps(response_content), 'utf-8')
    response.headers = {"content-type": content_type, "date": "Tue, 15 Nov 1994 12:45:26 GMT"}
    response.status_code = 404
    response.reason = "Not Found"
    response.url = "/uri"

    client = Client()
    with patch.object(
        client, "_deserialize", return_value=expected_result
    ):
    # Act
        result = client._deserialize_error(response)

    # Assert
    assert result == expected_result