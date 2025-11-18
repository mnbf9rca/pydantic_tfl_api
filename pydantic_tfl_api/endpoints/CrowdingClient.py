from ..core import ApiError, AsyncClient, Client, GenericResponseModel, ResponseModel
from .CrowdingClient_config import base_url, endpoints


class CrowdingClient(Client):
    """Information about crowding levels within Tfl Stations"""

    def Naptan(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan

  Query path: `/crowding/{Naptan}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['naptan'], params=[Naptan], endpoint_args=None)

    def Dayofweek(self, Naptan: str, DayOfWeek: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan for Day of Week

  Query path: `/crowding/{Naptan}/{DayOfWeek}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
    `DayOfWeek`: str - Day of week. Example: `Wed`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['dayofweek'], params=[Naptan, DayOfWeek], endpoint_args=None)

    def Live(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns live crowding information for Naptan

  Query path: `/crowding/{Naptan}/Live`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['live'], params=[Naptan], endpoint_args=None)


class AsyncCrowdingClient(AsyncClient):
    """Information about crowding levels within Tfl Stations"""

    async def Naptan(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan

  Query path: `/crowding/{Naptan}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['naptan'], params=[Naptan], endpoint_args=None)

    async def Dayofweek(self, Naptan: str, DayOfWeek: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns crowding information for Naptan for Day of Week

  Query path: `/crowding/{Naptan}/{DayOfWeek}`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
    `DayOfWeek`: str - Day of week. Example: `Wed`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['dayofweek'], params=[Naptan, DayOfWeek], endpoint_args=None)

    async def Live(self, Naptan: str) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Returns live crowding information for Naptan

  Query path: `/crowding/{Naptan}/Live`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
    `Naptan`: str - Naptan code. Example: `940GZZLUBND`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['live'], params=[Naptan], endpoint_args=None)

