from pydantic import BaseModel, ConfigDict, Field


class ActiveServiceType(BaseModel):
    mode: str | None = Field(None)
    serviceType: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
