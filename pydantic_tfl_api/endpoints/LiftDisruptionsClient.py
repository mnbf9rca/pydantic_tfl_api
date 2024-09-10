from .LiftDisruptionsClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import LiftDisruptionsArray

class LiftDisruptionsClient(Client):
    def get(self, ) -> ResponseModel[LiftDisruptionsArray] | ApiError:
        '''
        List of all currently disrupted lift routes

  Query path: `/Disruptions/Lifts/v2/`

  `ResponseModel.content` contains `models.LiftDisruptionsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['get'], endpoint_args=None)

