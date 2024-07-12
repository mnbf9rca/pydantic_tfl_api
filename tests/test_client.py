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
from pydantic_tfl_api.api_token import ApiToken
from pydantic_tfl_api.rest_client import RestClient
from pydantic_tfl_api.models.api_error import ApiError


# Mock models module
class MockModel(BaseModel):
    pass


class PydanticTestModel(BaseModel):
    name: str
    age: int
    content_expires: datetime | None = None


@pytest.mark.parametrize(
    "Model, response_json, result_expiry, expected_name, expected_age, expected_expiry",
    [
        # Happy path tests
        (
            PydanticTestModel,
            {"name": "Alice", "age": 30},
            datetime(2023, 12, 31),
            "Alice",
            30,
            datetime(2023, 12, 31),
        ),
        (PydanticTestModel, {"name": "Bob", "age": 25}, None, "Bob", 25, None),
        # Edge cases
        (
            PydanticTestModel,
            {"name": "", "age": 0},
            datetime(2023, 12, 31),
            "",
            0,
            datetime(2023, 12, 31),
        ),
        (PydanticTestModel, {"name": "Charlie", "age": -1}, None, "Charlie", -1, None),
        # Error cases
        (
            PydanticTestModel,
            {"name": "Alice"},
            datetime(2023, 12, 31),
            None,
            None,
            None,
        ),  # Missing age
        (
            PydanticTestModel,
            {"age": 30},
            datetime(2023, 12, 31),
            None,
            None,
            None,
        ),  # Missing name
        (
            PydanticTestModel,
            {"name": "Alice", "age": "thirty"},
            datetime(2023, 12, 31),
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
    Model, response_json, result_expiry, expected_name, expected_age, expected_expiry
):

    # Act
    if expected_name is None:
        with pytest.raises(ValidationError):
            Client._create_model_with_expiry(None, Model, response_json, result_expiry)
    else:
        instance = Client._create_model_with_expiry(
            None, Model, response_json, result_expiry
        )

        # Assert
        assert instance.name == expected_name
        assert instance.age == expected_age
        assert instance.content_expires == expected_expiry


@pytest.mark.parametrize(
    "api_token, expected_client_type, expected_models",
    [
        (None, RestClient, {"test_model"}),
        (ApiToken("valid_token", "valid_key"), RestClient, {"test_model"}),
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
        (
            "public, must-revalidate, max-age=43200, s-maxage=86400",
            86400,
        ),
        (
            "public, must-revalidate, max-age=43200",
            None,
        ),
        (
            None,
            None,
        ),
        (
            "public, must-revalidate, max-age=43200, s-maxage=-1",
            -1,
        ),
    ],
    ids=[
        "s-maxage_present",
        "s-maxage_absent",
        "no_cache_control_header",
        "negative_s-maxage_value",
    ],
)
def test_get_s_maxage_from_cache_control_header(cache_control_header, expected_result):
    # Mock Response
    response = Response()
    response.headers = {"cache-control": cache_control_header}

    # Act
    from pydantic_tfl_api.client import Client

    result = Client._get_s_maxage_from_cache_control_header(None, response)

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
    Response_Object.json.return_value = json.dumps(response_content)

    # Act

    client = Client()
    return_datetime = datetime(2024, 7, 12, 13, 00, 00)

    with patch.object(
        client, "_get_result_expiry", return_value=return_datetime
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
        MockModel, Response_Object.json.return_value, return_datetime
    )


@pytest.mark.parametrize(
    "s_maxage, date_header, expected_result",
    [
        (
            86400,
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            parsedate_to_datetime("Tue, 15 Nov 1994 12:45:26 GMT")
            + timedelta(seconds=86400),
        ),
        (
            None,
            {"date": "Tue, 15 Nov 1994 12:45:26 GMT"},
            None,
        ),
        (
            86400,
            {},
            None,
        ),
        (
            None,
            {},
            None,
        ),
    ],
    ids=[
        "s_maxage_and_date_present",
        "s_maxage_absent",
        "date_absent",
        "s_maxage_and_date_absent",
    ],
)
def test_get_result_expiry(s_maxage, date_header, expected_result):
    # Mock Response
    response = Response()
    response.headers.update(date_header)

    # Act
    client = Client()

    with patch.object(
        client, "_get_s_maxage_from_cache_control_header", return_value=s_maxage
    ):
        result = client._get_result_expiry(response)

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
    "Model, response_json, result_expiry, create_model_mock_return, expected_return",
    [
        (
            MockModel,
            {"name": "Alice", "age": 30},
            datetime(2023, 12, 31),
            "TestReturn1",
            "TestReturn1",
        ),
        (
            MockModel,
            [{"name": "Bob", "age": 30}, {"name": "Charlie", "age": 25}],
            datetime(2023, 12, 31),
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
    Model, response_json, result_expiry, create_model_mock_return, expected_return
):
    # Mock Client
    client = Client()

    # Mock _create_model_with_expiry
    with patch.object(
        client, "_create_model_with_expiry", return_value=create_model_mock_return
    ) as mock_create_model_with_expiry:

        # Act
        result = client._create_model_instance(Model, response_json, result_expiry)

        # Assert
        assert result == expected_return
        if isinstance(response_json, dict):
            mock_create_model_with_expiry.assert_called_with(
                Model, response_json, result_expiry
            )
        else:
            for item in response_json:
                mock_create_model_with_expiry.assert_any_call(Model, item, result_expiry)

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