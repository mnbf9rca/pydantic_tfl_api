from .VehicleClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import PredictionArray

class VehicleClient(Client):
    def GetByPathIds(self, ids: str) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Gets the predictions for a given list of vehicle Id's.

  Query path: `/Vehicle/{ids}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of vehicle ids e.g. LX58CFV,LX11AZB,LX58CFE. Max approx. 25 ids.. Example: `LX11AZB`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Vehicle_GetByPathIds'], params=[ids], endpoint_args=None)

