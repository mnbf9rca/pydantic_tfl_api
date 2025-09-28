from pydantic import RootModel, ConfigDict
from typing import List
from .Prediction import Prediction


class PredictionArray(RootModel[List[Prediction]]):

    model_config = ConfigDict(from_attributes=True)
