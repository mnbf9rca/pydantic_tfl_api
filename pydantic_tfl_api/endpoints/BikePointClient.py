from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import Place, PlaceArray
from .BikePointClient_config import base_url, endpoints


class BikePointClient(Client):
    """APIs relating to BikePoint and similar services"""

    def GetAll(self, ) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all bike point locations. The Place object has an addtionalProperties array which contains the nbBikes, nbDocks and nbSpaces
            numbers which give the status of the BikePoint. A mismatch in these numbers i.e. nbDocks - (nbBikes + nbSpaces) != 0 indicates broken docks.

  Query path: `/BikePoint/`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['BikePoint_GetAll'], endpoint_args=None)

    def Get(self, id: str) -> ResponseModel[Place] | ApiError:
        '''
        Gets the bike point with the given id.

  Query path: `/BikePoint/{id}`

  `ResponseModel.content` contains `models.Place` type.


  Parameters:
    `id`: str - A bike point id (a list of ids can be obtained from the above BikePoint call). Example: `BikePoints_583`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['BikePoint_Get'], params=[id], endpoint_args=None)

    def Search(self, query: str) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Search for bike stations by their name, a bike point's name often contains information about the name of the street
            or nearby landmarks, for example. Note that the search result does not contain the PlaceProperties i.e. the status
            or occupancy of the BikePoint, to get that information you should retrieve the BikePoint by its id on /BikePoint/id.

  Query path: `/BikePoint/Search`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `query`: str - The search term e.g. "St. James". Example: `London`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['BikePoint_Search'], endpoint_args={ 'query': query })


class AsyncBikePointClient(AsyncClient):
    """APIs relating to BikePoint and similar services"""

    async def GetAll(self, ) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all bike point locations. The Place object has an addtionalProperties array which contains the nbBikes, nbDocks and nbSpaces
            numbers which give the status of the BikePoint. A mismatch in these numbers i.e. nbDocks - (nbBikes + nbSpaces) != 0 indicates broken docks.

  Query path: `/BikePoint/`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['BikePoint_GetAll'], endpoint_args=None)

    async def Get(self, id: str) -> ResponseModel[Place] | ApiError:
        '''
        Gets the bike point with the given id.

  Query path: `/BikePoint/{id}`

  `ResponseModel.content` contains `models.Place` type.


  Parameters:
    `id`: str - A bike point id (a list of ids can be obtained from the above BikePoint call). Example: `BikePoints_583`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['BikePoint_Get'], params=[id], endpoint_args=None)

    async def Search(self, query: str) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Search for bike stations by their name, a bike point's name often contains information about the name of the street
            or nearby landmarks, for example. Note that the search result does not contain the PlaceProperties i.e. the status
            or occupancy of the BikePoint, to get that information you should retrieve the BikePoint by its id on /BikePoint/id.

  Query path: `/BikePoint/Search`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `query`: str - The search term e.g. "St. James". Example: `London`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['BikePoint_Search'], endpoint_args={ 'query': query })

