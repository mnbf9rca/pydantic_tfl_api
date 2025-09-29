from pydantic import RootModel, ConfigDict
from .Prediction import Prediction


class PredictionArray(RootModel[list[Prediction]]):

    model_config = ConfigDict(from_attributes=True)
