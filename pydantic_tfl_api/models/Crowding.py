from .PassengerFlow import PassengerFlow
from .TrainLoading import TrainLoading
from pydantic import BaseModel, Field, ConfigDict


class Crowding(BaseModel):
    passengerFlows: list[PassengerFlow] | None = Field(None)
    trainLoadings: list[TrainLoading] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
