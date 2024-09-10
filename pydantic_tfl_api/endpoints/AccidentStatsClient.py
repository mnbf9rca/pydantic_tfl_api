from .AccidentStatsClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import AccidentDetailArray

class AccidentStatsClient(Client):
    def Get(self, year: int) -> ResponseModel[AccidentDetailArray] | ApiError:
        '''
        Gets all accident details for accidents occuring in the specified year

  Query path: `/AccidentStats/{year}`

  `ResponseModel.content` contains `models.AccidentDetailArray` type.


  Parameters:
    `year`: int - Format - int32. The year for which to filter the accidents on.. Example: `2017`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AccidentStats_Get'], params=[year], endpoint_args=None)

