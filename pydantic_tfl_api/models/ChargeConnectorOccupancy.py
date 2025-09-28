from pydantic import BaseModel, Field, ConfigDict


class ChargeConnectorOccupancy(BaseModel):
    id: int | None = Field(None)
    sourceSystemPlaceId: str | None = Field(None)
    status: str | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
