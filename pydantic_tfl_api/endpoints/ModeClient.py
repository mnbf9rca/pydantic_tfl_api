from .ModeClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class ModeClient(Client):
    def GetActiveServiceTypes(self, ) -> ResponseModel | ApiError:
        '''
        Returns the service type active for a mode.
            Currently only supports tube

        ResponseModel.content contains `models.ActiveServiceTypesArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Mode_GetActiveServiceTypes'], endpoint_args=None)

    def Arrivals(self, mode: str, count: int | None = None) -> ResponseModel | ApiError:
        '''
        Gets the next arrival predictions for all stops of a given mode

        ResponseModel.content contains `models.PredictionArray` type.

        Parameters:
        mode: str - A mode name e.g. tube, dlr. Example: Tube
        count: int - Format - int32. A number of arrivals to return for each stop, -1 to return all available.. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Mode_Arrivals'], params=[mode], endpoint_args={ 'count': count })

