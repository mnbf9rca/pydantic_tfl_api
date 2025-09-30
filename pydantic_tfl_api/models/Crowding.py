from pydantic import BaseModel, ConfigDict, Field

from .PassengerFlow import PassengerFlow
from .TrainLoading import TrainLoading


class Crowding(BaseModel):
    passengerFlows: list[PassengerFlow] | None = Field(None, description="Busiest times at a station (static information)")
    trainLoadings: list[TrainLoading] | None = Field(None, description="Train Loading on a scale 1-6, 1 being \"Very quiet\" and 6 being \"Exceptionally busy\" (static information)")

    model_config = ConfigDict(from_attributes=True)
