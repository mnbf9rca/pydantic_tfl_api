from pydantic import BaseModel, ConfigDict, Field


class ChargeConnectorOccupancy(BaseModel):
    """"""

    id: int | None = Field(None, description="")
    sourceSystemPlaceId: str | None = Field(None, description="")
    status: str | None = Field(None, description="")

    model_config = ConfigDict(from_attributes=True)
