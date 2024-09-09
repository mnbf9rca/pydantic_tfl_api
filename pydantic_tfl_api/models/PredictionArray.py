from pydantic import RootModel
from typing import List
from .Prediction import Prediction


class PredictionArray(RootModel[List[Prediction]]):
    class Config:
        from_attributes = True

