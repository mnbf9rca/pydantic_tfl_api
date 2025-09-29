from pydantic import RootModel, ConfigDict
from typing import List
from .Prediction import Prediction


class PredictionArray(RootModel[list[Prediction]]):

    model_config = ConfigDict(from_attributes=True)
