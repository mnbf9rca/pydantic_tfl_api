from pydantic import RootModel
from typing import Any, Dict


class LondonAirForecast(RootModel[Dict[str, Any]]):

    model_config = {'from_attributes': True}
