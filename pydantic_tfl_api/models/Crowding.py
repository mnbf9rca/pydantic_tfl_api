from pydantic import BaseModel, ConfigDict, Field

from .PassengerFlow import PassengerFlow
from .TrainLoading import TrainLoading


class Crowding(BaseModel):
    passengerFlows: list[PassengerFlow] | None = Field(None)
    trainLoadings: list[TrainLoading] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
