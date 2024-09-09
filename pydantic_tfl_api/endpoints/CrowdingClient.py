from ..client import Client
from .CrowdingClient_config import endpoints
from .. import models
from ..models import ApiError

class CrowdingClient(Client):
    def naptan(self, Naptan: str) -> models.GenericResponseModel | ApiError:
        '''
        Returns crowding information for Naptan

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        '''
        return self._send_request_and_deserialize(endpoints['naptan'], params=[Naptan], endpoint_args=None)

    def dayofweek(self, Naptan: str, DayOfWeek: str) -> models.GenericResponseModel | ApiError:
        '''
        Returns crowding information for Naptan for Day of Week

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        DayOfWeek: str - Day of week. Example: Wed
        '''
        return self._send_request_and_deserialize(endpoints['dayofweek'], params=[Naptan, DayOfWeek], endpoint_args=None)

    def live(self, Naptan: str) -> models.GenericResponseModel | ApiError:
        '''
        Returns live crowding information for Naptan

        Parameters:
        Naptan: str - Naptan code. Example: 940GZZLUBND
        '''
        return self._send_request_and_deserialize(endpoints['live'], params=[Naptan], endpoint_args=None)

