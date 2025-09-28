from pydantic import BaseModel, Field, ConfigDict


class Bay(BaseModel):
    bayType: str | None = Field(None)
    bayCount: int | None = Field(None)
    free: int | None = Field(None)
    occupied: int | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
