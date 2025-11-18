from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import PredictionArray
from .VehicleClient_config import base_url, endpoints


class VehicleClient(Client):
    """APIs relating to Vehicle and similar services"""

    def GetByPathIds(self, ids: str) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Gets the predictions for a given list of vehicle Id's.

  Query path: `/Vehicle/{ids}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of vehicle ids e.g. LX58CFV,LX11AZB,LX58CFE. Max approx. 25 ids.. Example: `LX11AZB`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Vehicle_GetByPathIds'], params=[ids], endpoint_args=None)


class AsyncVehicleClient(AsyncClient):
    """APIs relating to Vehicle and similar services"""

    async def GetByPathIds(self, ids: str) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Gets the predictions for a given list of vehicle Id's.

  Query path: `/Vehicle/{ids}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `ids`: str - A comma-separated list of vehicle ids e.g. LX58CFV,LX11AZB,LX58CFE. Max approx. 25 ids.. Example: `LX11AZB`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Vehicle_GetByPathIds'], params=[ids], endpoint_args=None)

