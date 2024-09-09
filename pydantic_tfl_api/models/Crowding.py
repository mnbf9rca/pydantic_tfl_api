from pydantic import BaseModel, Field
from .PassengerFlow import PassengerFlow
from .TrainLoading import TrainLoading
from pydantic import BaseModel, Field
from typing import List, Optional


class Crowding(BaseModel):
    passengerFlows: Optional[List[PassengerFlow]] = Field(None, alias='passengerFlows')
    trainLoadings: Optional[List[TrainLoading]] = Field(None, alias='trainLoadings')

    class Config:
        from_attributes = True
