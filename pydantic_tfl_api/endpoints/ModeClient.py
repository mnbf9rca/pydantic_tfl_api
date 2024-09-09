from ..client import Client
from .ModeClient_config import endpoints
from .. import models
from ..models import ApiError

class ModeClient(Client):
    def getactiveservicetypes(self, ) -> models.ActiveServiceTypesArray | ApiError:
        '''
        Returns the service type active for a mode.
            Currently only supports tube

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Mode_GetActiveServiceTypes'], endpoint_args=None)

    def arrivals(self, mode: str, count: int | None = None) -> models.PredictionArray | ApiError:
        '''
        Gets the next arrival predictions for all stops of a given mode

        Parameters:
        mode: str - A mode name e.g. tube, dlr. Example: Tube
        count: int - Format - int32. A number of arrivals to return for each stop, -1 to return all available.. Example: None given
        '''
        return self._send_request_and_deserialize(endpoints['Mode_Arrivals'], params=[mode], endpoint_args={ 'count': count })

