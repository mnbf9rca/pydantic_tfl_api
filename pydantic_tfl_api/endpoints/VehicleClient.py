from ..client import Client
from .VehicleClient_config import endpoints
from .. import models
from ..models import ApiError

class VehicleClient(Client):
    def getbypathids(self, ids: str) -> models.PredictionArray | ApiError:
        '''
        Gets the predictions for a given list of vehicle Id's.

        Parameters:
        ids: str - A comma-separated list of vehicle ids e.g. LX58CFV,LX11AZB,LX58CFE. Max approx. 25 ids.. Example: LX11AZB
        '''
        return self._send_request_and_deserialize(endpoints['Vehicle_GetByPathIds'], params=[ids], endpoint_args=None)

