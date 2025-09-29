from pydantic import BaseModel, ConfigDict, Field


class OrderedRoute(BaseModel):
    name: str | None = Field(None)
    naptanIds: list[str] | None = Field(None)
    serviceType: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
