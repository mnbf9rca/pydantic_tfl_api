"""Shared pytest fixtures for test suite.

This module provides reusable fixtures for mocking HTTP responses
that conform to the HTTPResponse protocol, enabling tests to work
with any HTTP backend (httpx or requests).
"""

import json
from collections.abc import Callable
from unittest.mock import Mock

import pytest

from pydantic_tfl_api.core.http_client import HTTPResponse


@pytest.fixture
def mock_http_response_factory() -> Callable[..., Mock]:
    """Factory fixture for creating mock HTTPResponse protocol-compliant objects.

    Returns a factory function that creates Mock objects conforming to the
    HTTPResponse protocol. Use this when you need to test code that works
    with any HTTP backend.

    Example:
        def test_something(mock_http_response_factory):
            response = mock_http_response_factory(
                status_code=200,
                headers={"Content-Type": "application/json"},
                text='{"key": "value"}'
            )
            # response conforms to HTTPResponse protocol
    """
    def create(
        status_code: int = 200,
        headers: dict[str, str] | None = None,
        text: str = "",
        url: str = "http://test.com",
        reason: str = "OK",
        json_data: dict[str, object] | list[object] | None = None,
    ) -> Mock:
        mock = Mock(spec=HTTPResponse)
        mock.status_code = status_code
        mock.headers = headers or {}
        mock.text = text
        mock.url = url
        mock.reason = reason

        # Handle json() method
        if json_data is not None:
            mock.json.return_value = json_data
        elif text:
            try:
                mock.json.return_value = json.loads(text)
            except (json.JSONDecodeError, ValueError):
                mock.json.return_value = {}
        else:
            mock.json.return_value = {}

        return mock

    return create


@pytest.fixture
def http_response_from_json_factory() -> Callable[[str], Mock]:
    """Factory fixture for creating mock HTTPResponse from JSON files.

    Returns a factory function that loads a serialized response from a JSON
    file and creates a protocol-compliant mock. Used for testing with
    recorded TfL API responses.

    Example:
        def test_deserialize(http_response_from_json_factory):
            response = http_response_from_json_factory("tests/tfl_responses/line.json")
            result = client._deserialize(model_name, response)
    """
    def create(json_file: str) -> Mock:
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

    return create
