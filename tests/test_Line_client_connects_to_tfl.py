import pytest

from pydantic_tfl_api.core import ApiError, ResponseModel
from pydantic_tfl_api.endpoints import AsyncLineClient, LineClient
from pydantic_tfl_api.models import Line, LineArray


def test_get_line_status_by_mode_rejected_with_invalid_api_key() -> None:
    api_token = "your_app_key"
    client = LineClient(api_token)
    assert client.client.app_key is not None and client.client.app_key["app_key"] == api_token
    # should get a 429 error inside an ApiError object
    result = client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("overground,tube")
    assert isinstance(result, ApiError)
    assert result.http_status_code == 429
    assert result.http_status == "Invalid App Key"


def test_get_line_status_by_mode() -> None:
    # this API doesnt need authentication so we can use it to test that the API is working
    test_client = LineClient()
    # should get a list of Line objects
    result = test_client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("overground,tube")
    assert isinstance(result, ResponseModel)
    response_content = result.content
    assert isinstance(response_content, LineArray)
    assert hasattr(response_content, "root")
    assert len(response_content.root) > 0
    # check that each item in the list is a Line object
    for item in response_content.root:
        assert isinstance(item, Line)


# Async client tests - same tests but using the async client


@pytest.mark.asyncio
async def test_async_get_line_status_by_mode_rejected_with_invalid_api_key() -> None:
    """Test that async client handles invalid API key correctly."""
    api_token = "your_app_key"
    client = AsyncLineClient(api_token)
    assert client.client.app_key is not None and client.client.app_key["app_key"] == api_token
    # should get a 429 error inside an ApiError object
    result = await client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("overground,tube")
    assert isinstance(result, ApiError)
    assert result.http_status_code == 429
    assert result.http_status == "Invalid App Key"


@pytest.mark.asyncio
async def test_async_get_line_status_by_mode() -> None:
    """Test that async client can fetch real data from TfL API."""
    # this API doesnt need authentication so we can use it to test that the API is working
    test_client = AsyncLineClient()
    # should get a list of Line objects
    result = await test_client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("overground,tube")
    assert isinstance(result, ResponseModel)
    response_content = result.content
    assert isinstance(response_content, LineArray)
    assert hasattr(response_content, "root")
    assert len(response_content.root) > 0
    # check that each item in the list is a Line object
    for item in response_content.root:
        assert isinstance(item, Line)
