from pydantic import BaseModel, ConfigDict, Field


class LiftDisruption(BaseModel):
    icsCode: str | None = Field(None, description="Ics code for the disrupted lift route")
    naptanCode: str | None = Field(None, description="Naptan code for the stop area of the disrupted lift route")
    stopPointName: str | None = Field(None, description="Name of the stop point of the disrupted lift route")
    outageStartArea: str | None = Field(None, description="Id for the start of the disrupted lift route")
    outageEndArea: str | None = Field(None, description="Id for the end of the disrupted lift route")
    message: str | None = Field(None, description="Customer facing message for the disrupted lift route")

    model_config = ConfigDict(from_attributes=True)
