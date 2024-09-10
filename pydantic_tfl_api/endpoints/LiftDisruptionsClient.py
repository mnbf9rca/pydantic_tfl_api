from .LiftDisruptionsClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class LiftDisruptionsClient(Client):
    def get(self, ) -> ResponseModel | ApiError:
        '''
        List of all currently disrupted lift routes

        ResponseModel.content contains `models.LiftDisruptionsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['get'], endpoint_args=None)

