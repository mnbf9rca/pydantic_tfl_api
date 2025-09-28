from pydantic import BaseModel, Field, ConfigDict


class LineServiceTypeInfo(BaseModel):
    name: str | None = Field(None)
    uri: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
