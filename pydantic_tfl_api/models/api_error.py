from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from email.utils import parsedate_to_datetime

class ApiError(BaseModel):
    timestamp_utc: datetime = Field(alias='timestampUtc')
    exception_type: str = Field(alias='exceptionType')
    http_status_code: int = Field(alias='httpStatusCode')
    http_status: str = Field(alias='httpStatus')
    relative_uri: str = Field(alias='relativeUri')
    message: str = Field(alias='message')

    @field_validator('timestamp_utc', mode='before')
    def parse_timestamp(cls, v):
        return v if isinstance(v, datetime) else parsedate_to_datetime(v)
        # return datetime.strptime(v, '%a, %d %b %Y %H:%M:%S %Z')

    model_config = {'populate_by_name': True}
