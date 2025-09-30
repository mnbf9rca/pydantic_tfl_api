from datetime import datetime
from email.utils import parsedate_to_datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field, RootModel, field_validator

# Define a type variable for the content
T = TypeVar("T", bound=BaseModel)


class ResponseModel(BaseModel, Generic[T]):
    content_expires: datetime | None
    shared_expires: datetime | None
    response_timestamp: datetime | None
    content: T  # The content will now be of the specified type

    model_config = ConfigDict(from_attributes=True)


class GenericResponseModel(RootModel[Any]):
    """
    Universal model for unstructured API responses.

    This model serves as a fallback for endpoints that return unstructured
    or dynamic content that cannot be modeled with specific Pydantic classes.
    Examples include proxy endpoints, meta endpoints, and undocumented responses.

    Uses default configuration which is sufficient for handling any JSON
    data structure returned by the TfL API.
    """

    model_config = ConfigDict(from_attributes=True)


class ApiError(BaseModel):
    """
    Enhanced API error model with comprehensive debugging context.

    Provides detailed information about API errors including the original
    TfL error response plus additional context for debugging and monitoring.
    """

    # TfL API error fields
    timestamp_utc: datetime = Field(alias="timestampUtc")
    exception_type: str = Field(alias="exceptionType")
    http_status_code: int = Field(alias="httpStatusCode")
    http_status: str = Field(alias="httpStatus")
    relative_uri: str = Field(alias="relativeUri")
    message: str = Field(alias="message")

    # Extended context fields for debugging
    request_method: str | None = Field(None, description="HTTP method used (GET, POST, etc.)")
    request_url: str | None = Field(None, description="Full URL of the failed request")
    request_headers: dict[str, str] | None = Field(None, description="Request headers (sensitive data filtered)")
    response_body: str | None = Field(None, description="Raw response body for debugging")
    retry_count: int | None = Field(None, description="Number of retries attempted")
    error_category: str | None = Field(
        None,
        description="Error category: network, authentication, rate_limit, client_error, server_error, timeout, unknown",
    )

    @field_validator("timestamp_utc", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        return v if isinstance(v, datetime) else parsedate_to_datetime(v)
        # return datetime.strptime(v, '%a, %d %b %Y %H:%M:%S %Z')

    model_config = ConfigDict(populate_by_name=True)
