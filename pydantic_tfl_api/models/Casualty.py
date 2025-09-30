from pydantic import BaseModel, ConfigDict, Field


class Casualty(BaseModel):
    age: int | None = Field(None)
    class_field: str | None = Field(None, alias='class')
    severity: str | None = Field(None)
    mode: str | None = Field(None)
    ageBand: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
