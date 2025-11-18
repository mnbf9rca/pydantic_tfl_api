from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import LiftDisruptionsArray
from .LiftDisruptionsClient_config import base_url, endpoints


class LiftDisruptionsClient(Client):
    """APIs relating to Lift disruptions at Transport for London Stations"""

    def Get(self, ) -> ResponseModel[LiftDisruptionsArray] | ApiError:
        '''
        List of all currently disrupted lift routes

  Query path: `/Disruptions/Lifts/v2/`

  `ResponseModel.content` contains `models.LiftDisruptionsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['get'], endpoint_args=None)


class AsyncLiftDisruptionsClient(AsyncClient):
    """APIs relating to Lift disruptions at Transport for London Stations"""

    async def Get(self, ) -> ResponseModel[LiftDisruptionsArray] | ApiError:
        '''
        List of all currently disrupted lift routes

  Query path: `/Disruptions/Lifts/v2/`

  `ResponseModel.content` contains `models.LiftDisruptionsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['get'], endpoint_args=None)

