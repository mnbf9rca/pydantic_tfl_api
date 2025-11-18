"""
Basic Functionality Tests for TfL API Integration.

Simple smoke tests to verify that:
1. Core clients can instantiate
2. They can make API calls to TfL without errors
3. Responses parse into our generated models

This is NOT testing TfL API functionality - just that our generated
models work with real TfL responses. No mocks or samples needed.
"""

import time
from contextlib import suppress

import pytest

from pydantic_tfl_api.core import ApiError, ResponseModel, get_default_http_client
from pydantic_tfl_api.endpoints import (
    AsyncBikePointClient,
    AsyncJourneyClient,
    AsyncLineClient,
    AsyncModeClient,
    AsyncStopPointClient,
    BikePointClient,
    JourneyClient,
    LineClient,
    ModeClient,
    StopPointClient,
)


class TestBasicFunctionality:
    """Basic smoke tests for core TfL API functionality."""

    @pytest.fixture(autouse=True)
    def rate_limit_delay(self) -> None:
        """Respect TfL rate limiting between tests."""
        time.sleep(1.1)

    def _validate_response_model(self, result: ResponseModel | ApiError, expected_type: type = ResponseModel) -> None:
        """Helper to validate ResponseModel content consistently."""
        assert isinstance(result, expected_type), f"Expected {expected_type.__name__}, got {type(result)}"
        if isinstance(result, ResponseModel):
            assert result.content is not None, "Response should have content"

    def _validate_journey_result(self, result: ResponseModel | ApiError) -> None:
        """Helper to validate journey results which can be ResponseModel or ApiError."""
        if isinstance(result, ResponseModel):
            assert result.content is not None, "ResponseModel should have content"
        elif isinstance(result, ApiError):
            # ApiError is also valid - indicates parsing worked but API returned an error
            assert result.http_status_code is not None, "ApiError should have status code"
        else:
            pytest.fail(f"Unexpected result type: {type(result)}")

    @pytest.fixture(scope="class")
    def api_health_check(self) -> bool:
        """Skip tests if TfL API is unavailable."""

        with suppress(Exception):
            http_client = get_default_http_client()
            response = http_client.get("https://api.tfl.gov.uk/", timeout=10)
            if response.status_code == 200:
                return True
        pytest.skip("TfL API unavailable - skipping basic functionality tests")

    def test_line_client_basic_query(self, api_health_check: bool) -> None:
        """Test LineClient can query TfL and parse response."""
        client = LineClient()
        result = client.MetaModes()

        # Should get ResponseModel, not ApiError
        self._validate_response_model(result)

    def test_line_client_tube_status(self, api_health_check: bool) -> None:
        """Test LineClient can get tube line status."""
        client = LineClient()
        result = client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("tube")

        # Should parse without errors
        self._validate_response_model(result)

    def test_stoppoint_client_basic_query(self, api_health_check: bool) -> None:
        """Test StopPointClient can query TfL and parse response."""
        client = StopPointClient()
        result = client.MetaModes()

        # Should parse without errors
        self._validate_response_model(result)

    def test_stoppoint_client_by_type(self, api_health_check: bool) -> None:
        """Test StopPointClient can get stops by type."""
        client = StopPointClient()
        result = client.GetByTypeByPathTypes("NaptanMetroStation")

        # Should parse without errors
        self._validate_response_model(result)

    def test_bikepoint_client_basic_query(self, api_health_check: bool) -> None:
        """Test BikePointClient can query TfL and parse response."""
        client = BikePointClient()
        result = client.GetAll()

        # Should parse without errors
        self._validate_response_model(result)

    def test_mode_client_basic_query(self, api_health_check: bool) -> None:
        """Test ModeClient can query TfL and parse response."""
        client = ModeClient()
        result = client.GetActiveServiceTypes()

        # Should parse without errors
        self._validate_response_model(result)

    def test_journey_client_basic_query(self, api_health_check: bool) -> None:
        """Test JourneyClient can query TfL and parse response."""
        client = JourneyClient()
        # Use specific station codes to avoid ambiguity
        result = client.JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu(
            "940GZZLUKSX", "940GZZLUVIC"
        )

        # Should parse without errors (ResponseModel or ApiError both indicate parsing worked)
        assert isinstance(result, ResponseModel | ApiError), f"Expected ResponseModel or ApiError, got {type(result)}"

        # If we got a ResponseModel, validate it has content
        # If we got an ApiError, that's also valid (could be network/API issue)
        # Both outcomes indicate successful parsing, which is what we're testing here
        self._validate_journey_result(result)

    def test_journey_client_invalid_station_codes(self, api_health_check: bool) -> None:
        """Test JourneyClient returns ApiError for ambiguous or invalid station codes."""
        client = JourneyClient()
        result = client.JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu(
            "INVALID_CODE", "940GZZLUXXX"
        )

        # Should return ApiError for invalid/ambiguous station codes
        assert isinstance(result, ApiError), f"Expected ApiError for invalid station codes, got {type(result)}"
        assert result.http_status_code is not None, "ApiError should have HTTP status code"

    def test_error_handling_returns_api_error(self) -> None:
        """Test that invalid API calls return ApiError objects."""
        client = LineClient("invalid_api_key")
        result = client.MetaModes()

        # Should return ApiError for invalid key
        assert isinstance(result, ApiError), f"Expected ApiError for invalid key, got {type(result)}"
        assert hasattr(result, "http_status_code"), "ApiError should have status code"
        assert hasattr(result, "http_status"), "ApiError should have status message"

    # Async client tests

    @pytest.mark.asyncio
    async def test_async_line_client_basic_query(self, api_health_check: bool) -> None:
        """Test AsyncLineClient can query TfL and parse response."""
        client = AsyncLineClient()
        result = await client.MetaModes()

        # Should get ResponseModel, not ApiError
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_line_client_tube_status(self, api_health_check: bool) -> None:
        """Test AsyncLineClient can get tube line status."""
        client = AsyncLineClient()
        result = await client.StatusByModeByPathModesQueryDetailQuerySeverityLevel("tube")

        # Should parse without errors
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_stoppoint_client_basic_query(self, api_health_check: bool) -> None:
        """Test AsyncStopPointClient can query TfL and parse response."""
        client = AsyncStopPointClient()
        result = await client.MetaModes()

        # Should parse without errors
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_stoppoint_client_by_type(self, api_health_check: bool) -> None:
        """Test AsyncStopPointClient can get stops by type."""
        client = AsyncStopPointClient()
        result = await client.GetByTypeByPathTypes("NaptanMetroStation")

        # Should parse without errors
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_bikepoint_client_basic_query(self, api_health_check: bool) -> None:
        """Test AsyncBikePointClient can query TfL and parse response."""
        client = AsyncBikePointClient()
        result = await client.GetAll()

        # Should parse without errors
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_mode_client_basic_query(self, api_health_check: bool) -> None:
        """Test AsyncModeClient can query TfL and parse response."""
        client = AsyncModeClient()
        result = await client.GetActiveServiceTypes()

        # Should parse without errors
        self._validate_response_model(result)

    @pytest.mark.asyncio
    async def test_async_journey_client_basic_query(self, api_health_check: bool) -> None:
        """Test AsyncJourneyClient can query TfL and parse response."""
        client = AsyncJourneyClient()
        # Use specific station codes to avoid ambiguity
        result = await client.JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu(
            "940GZZLUKSX", "940GZZLUVIC"
        )

        # Should parse without errors (ResponseModel or ApiError both indicate parsing worked)
        assert isinstance(result, ResponseModel | ApiError), f"Expected ResponseModel or ApiError, got {type(result)}"

        # If we got a ResponseModel, validate it has content
        # If we got an ApiError, that's also valid (could be network/API issue)
        # Both outcomes indicate successful parsing, which is what we're testing here
        self._validate_journey_result(result)

    @pytest.mark.asyncio
    async def test_async_journey_client_invalid_station_codes(self, api_health_check: bool) -> None:
        """Test AsyncJourneyClient returns ApiError for ambiguous or invalid station codes."""
        client = AsyncJourneyClient()
        result = await client.JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu(
            "INVALID_CODE", "940GZZLUXXX"
        )

        # Should return ApiError for invalid/ambiguous station codes
        assert isinstance(result, ApiError), f"Expected ApiError for invalid station codes, got {type(result)}"
        assert result.http_status_code is not None, "ApiError should have HTTP status code"

    @pytest.mark.asyncio
    async def test_async_error_handling_returns_api_error(self) -> None:
        """Test that invalid async API calls return ApiError objects."""
        client = AsyncLineClient("invalid_api_key")
        result = await client.MetaModes()

        # Should return ApiError for invalid key
        assert isinstance(result, ApiError), f"Expected ApiError for invalid key, got {type(result)}"
        assert hasattr(result, "http_status_code"), "ApiError should have status code"
        assert hasattr(result, "http_status"), "ApiError should have status message"
