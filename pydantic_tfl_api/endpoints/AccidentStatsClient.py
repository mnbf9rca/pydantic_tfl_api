from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import AccidentDetailArray
from .AccidentStatsClient_config import base_url, endpoints


class AccidentStatsClient(Client):
    """APIs relating to AccidentStats and similar services"""

    def Get(self, year: int) -> ResponseModel[AccidentDetailArray] | ApiError:
        '''
        Gets all accident details for accidents occuring in the specified year

  Query path: `/AccidentStats/{year}`

  `ResponseModel.content` contains `models.AccidentDetailArray` type.


  Parameters:
    `year`: int - Format - int32. The year for which to filter the accidents on.. Example: `2017`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AccidentStats_Get'], params=[year], endpoint_args=None)


class AsyncAccidentStatsClient(AsyncClient):
    """APIs relating to AccidentStats and similar services"""

    async def Get(self, year: int) -> ResponseModel[AccidentDetailArray] | ApiError:
        '''
        Gets all accident details for accidents occuring in the specified year

  Query path: `/AccidentStats/{year}`

  `ResponseModel.content` contains `models.AccidentDetailArray` type.


  Parameters:
    `year`: int - Format - int32. The year for which to filter the accidents on.. Example: `2017`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['AccidentStats_Get'], params=[year], endpoint_args=None)

