from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import ActiveServiceTypesArray, PredictionArray
from .ModeClient_config import base_url, endpoints


class ModeClient(Client):
    """APIs relating to Mode and similar services"""

    def GetActiveServiceTypes(self, ) -> ResponseModel[ActiveServiceTypesArray] | ApiError:
        '''
        Returns the service type active for a mode.
            Currently only supports tube

  Query path: `/Mode/ActiveServiceTypes`

  `ResponseModel.content` contains `models.ActiveServiceTypesArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Mode_GetActiveServiceTypes'], endpoint_args=None)

    def Arrivals(self, mode: str, count: int | None = None) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Gets the next arrival predictions for all stops of a given mode

  Query path: `/Mode/{mode}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `mode`: str - A mode name e.g. tube, dlr. Example: `Tube`
    `count`: int - Format - int32. A number of arrivals to return for each stop, -1 to return all available..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Mode_Arrivals'], params=[mode], endpoint_args={ 'count': count })


class AsyncModeClient(AsyncClient):
    """APIs relating to Mode and similar services"""

    async def GetActiveServiceTypes(self, ) -> ResponseModel[ActiveServiceTypesArray] | ApiError:
        '''
        Returns the service type active for a mode.
            Currently only supports tube

  Query path: `/Mode/ActiveServiceTypes`

  `ResponseModel.content` contains `models.ActiveServiceTypesArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Mode_GetActiveServiceTypes'], endpoint_args=None)

    async def Arrivals(self, mode: str, count: int | None = None) -> ResponseModel[PredictionArray] | ApiError:
        '''
        Gets the next arrival predictions for all stops of a given mode

  Query path: `/Mode/{mode}/Arrivals`

  `ResponseModel.content` contains `models.PredictionArray` type.


  Parameters:
    `mode`: str - A mode name e.g. tube, dlr. Example: `Tube`
    `count`: int - Format - int32. A number of arrivals to return for each stop, -1 to return all available..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Mode_Arrivals'], params=[mode], endpoint_args={ 'count': count })

