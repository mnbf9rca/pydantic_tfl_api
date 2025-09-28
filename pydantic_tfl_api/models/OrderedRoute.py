from pydantic import BaseModel, Field, ConfigDict


class OrderedRoute(BaseModel):
    name: str | None = Field(None)
    naptanIds: list[str] | None = Field(None)
    serviceType: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
