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
    timestamp_utc: datetime = Field(alias="timestampUtc")
    exception_type: str = Field(alias="exceptionType")
    http_status_code: int = Field(alias="httpStatusCode")
    http_status: str = Field(alias="httpStatus")
    relative_uri: str = Field(alias="relativeUri")
    message: str = Field(alias="message")

    @field_validator("timestamp_utc", mode="before")
    @classmethod
    def parse_timestamp(cls, v: Any) -> datetime:
        return v if isinstance(v, datetime) else parsedate_to_datetime(v)
        # return datetime.strptime(v, '%a, %d %b %Y %H:%M:%S %Z')

    model_config = {"populate_by_name": True}
