from .PassengerFlow import PassengerFlow
from .TrainLoading import TrainLoading
from pydantic import BaseModel, Field
from typing import List, Optional


class Crowding(BaseModel):
    passengerFlows: Optional[list[PassengerFlow]] = Field(None, alias='passengerFlows')
    trainLoadings: Optional[list[TrainLoading]] = Field(None, alias='trainLoadings')

    model_config = {'from_attributes': True}
