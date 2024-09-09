from ..client import Client
from .AccidentStatsClient_config import endpoints
from .. import models
from ..models import ApiError

class AccidentStatsClient(Client):
    def get(self, year: int) -> models.AccidentDetailArray | ApiError:
        '''
        Gets all accident details for accidents occuring in the specified year

        Parameters:
        year: int - Format - int32. The year for which to filter the accidents on.. Example: 2017
        '''
        return self._send_request_and_deserialize(endpoints['AccidentStats_Get'], params=[year], endpoint_args=None)

