import pytest
import json
from unittest.mock import Mock, patch, MagicMock
from requests.models import Response

# from importlib import import_module
# import pkgutil

from pydantic import BaseModel, ValidationError
from datetime import datetime, timedelta

from pydantic_tfl_api.client import Client
from pydantic_tfl_api.api_token import ApiToken
from pydantic_tfl_api.rest_client import RestClient


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


# Mock models module
class MockModel(BaseModel):
    pass


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
