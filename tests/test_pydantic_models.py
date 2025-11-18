# this suite tests that the pydantic models can deserialise the JSON responses from the TFL API
# it uses snapshot responses from the API on a day that there was some disruption etc.

import json
import unittest
from typing import get_args
from unittest.mock import Mock

from pydantic import BaseModel, RootModel, TypeAdapter

from pydantic_tfl_api import models
from pydantic_tfl_api.core import Client, ResponseModel
from pydantic_tfl_api.core.http_client import HTTPResponse

from .config_for_tests import response_to_request_mapping


def create_response_from_json(json_file: str) -> Mock:
    """Create a mock HTTPResponse from a JSON file.

    This creates a protocol-compliant mock that works with any HTTP backend.
    """
    with open(json_file) as f:
        serialised_response = json.load(f)

    # Parse content
    content_str = serialised_response["content"]
    try:
        content_data = json.loads(content_str)
    except (json.JSONDecodeError, ValueError):
        content_data = {}

    mock = Mock(spec=HTTPResponse)
    mock.headers = serialised_response["headers"]
    mock.status_code = serialised_response["status_code"]
    mock.url = serialised_response["url"]
    mock.text = content_str
    mock.reason = "OK"
    mock.json.return_value = content_data

    return mock


def get_and_save_response(response: BaseModel | list[BaseModel], file_name: str) -> None:
    """
    this is the method that was used to serialise the Pydantic models
    so that we can use them as expected responses in the tests
    it's not used in the tests, but it's here for reference
    """
    if response is None:
        return
    content = [r.model_dump_json() for r in response] if isinstance(response, list) else response.model_dump_json()

    with open(file_name, "w") as file:
        file.write(json.dumps(content))


def load_and_validate_expected_response(file_name: str, model: type[BaseModel]) -> BaseModel:
    with open(file_name) as file:
        content = json.load(file)
    if isinstance(model, type) and issubclass(model, RootModel):
        content_adapter = TypeAdapter(model)
        return content_adapter.validate_python(content)

    return model.model_validate(content)


def _validate_root_model_if_applicable(
    response_content: BaseModel | list[BaseModel], expect_empty_response: bool
) -> None:
    """Helper to validate root model structure without conditionals in main test."""
    is_root_model = isinstance(response_content, type) and issubclass(response_content, RootModel)
    if not is_root_model:
        return  # Not a root model, nothing to validate

    # Check if this is a root model and that it has a root attribute
    assert hasattr(response_content, "root")
    # Assert that result is not empty only if we expect it not to be
    assert (not expect_empty_response and response_content.root) or (
        expect_empty_response and not response_content.root
    )


class TestTypeHints(unittest.TestCase):
    def test_model_literal(self) -> None:
        # models.ResponseModelName is a Literal which should contain the names of all the models in the package
        # this test checks that the names are correct, none are missing.
        # we do this by comparing the __all__ attribute of the models module with the literal

        self.assertListEqual(list(get_args(models.ResponseModelName)), models.__all__)


for resp in response_to_request_mapping:

    def test_deserialise_response(resp: str = resp) -> None:
        response = create_response_from_json(f"tests/tfl_responses/{resp}.json")
        expect_empty_response: bool = bool(response_to_request_mapping[resp]["result_is_empty"])
        model = response_to_request_mapping[resp]["model"]

        test_client = Client()
        model_object = test_client._get_model(model)

        result = test_client._deserialize(model, response)
        assert isinstance(result, ResponseModel)

        response_content = result.content
        expected_result = load_and_validate_expected_response(f"tests/tfl_responses/{resp}_expected.json", model_object)

        assert response_content == expected_result

        # Validate root model structure if applicable
        _validate_root_model_if_applicable(response_content, expect_empty_response)

    globals()[f"test_deserialise_response_{resp}"] = test_deserialise_response

# def save_result(result: BaseModel, resp: str):
#     with open(f"tests/tfl_responses/{resp}_expected.json", "w") as file:
#         file.write(result.model_dump_json(by_alias=True))
