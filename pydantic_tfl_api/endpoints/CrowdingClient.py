from .CrowdingClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class CrowdingClient(Client):
    def naptan(self, Naptan: str) -> ResponseModel | ApiError:
        '''
        Returns crowding information for Naptan

        ResponseModel.content contains `models.GenericResponseModel` type.

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        '''
        return self._send_request_and_deserialize(base_url, endpoints['naptan'], params=[Naptan], endpoint_args=None)

    def dayofweek(self, Naptan: str, DayOfWeek: str) -> ResponseModel | ApiError:
        '''
        Returns crowding information for Naptan for Day of Week

        ResponseModel.content contains `models.GenericResponseModel` type.

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        DayOfWeek: str - Day of week. Example: Wed
        '''
        return self._send_request_and_deserialize(base_url, endpoints['dayofweek'], params=[Naptan, DayOfWeek], endpoint_args=None)

    def live(self, Naptan: str) -> ResponseModel | ApiError:
        '''
        Returns live crowding information for Naptan

        ResponseModel.content contains `models.GenericResponseModel` type.

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        '''
        return self._send_request_and_deserialize(base_url, endpoints['live'], params=[Naptan], endpoint_args=None)

