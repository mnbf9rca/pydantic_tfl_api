from .CrowdingClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import GenericResponseModel

class CrowdingClient(Client):
    def naptan(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan

  Query path: `/crowding/{Naptan}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['naptan'], params=[Naptan], endpoint_args=None)

    def dayofweek(self, Naptan: str, DayOfWeek: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan for Day of Week

  Query path: `/crowding/{Naptan}/{DayOfWeek}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
    `DayOfWeek`: str - Day of week. Example: `Wed`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['dayofweek'], params=[Naptan, DayOfWeek], endpoint_args=None)

    def live(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns live crowding information for Naptan

  Query path: `/crowding/{Naptan}/Live`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['live'], params=[Naptan], endpoint_args=None)

