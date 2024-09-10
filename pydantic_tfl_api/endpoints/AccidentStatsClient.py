from .AccidentStatsClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class AccidentStatsClient(Client):
    def get(self, year: int) -> ResponseModel | ApiError:
        '''
        Gets all accident details for accidents occuring in the specified year

        ResponseModel.content contains `models.AccidentDetailArray` type.

        Parameters:
        year: int - Format - int32. The year for which to filter the accidents on.. Example: 2017
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AccidentStats_Get'], params=[year], endpoint_args=None)

