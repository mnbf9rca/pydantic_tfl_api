from pydantic import BaseModel, ConfigDict, Field


class ValidityPeriod(BaseModel):
    """Represents a period for which a planned works is valid."""

    fromDate: str | None = Field(None, description="Gets or sets the start date.")
    toDate: str | None = Field(None, description="Gets or sets the end date.")
    isNow: bool | None = Field(None, description="If true is a realtime status rather than planned or info")

    model_config = ConfigDict(from_attributes=True)
