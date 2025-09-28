from pydantic import BaseModel, Field, ConfigDict


class ValidityPeriod(BaseModel):
    fromDate: str | None = Field(None)
    toDate: str | None = Field(None)
    isNow: bool | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
