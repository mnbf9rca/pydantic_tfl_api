from pydantic import RootModel
from typing import List
from .Prediction import Prediction


class PredictionArray(RootModel[List[Prediction]]):

    model_config = {'from_attributes': True}
