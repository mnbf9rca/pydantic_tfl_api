from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import SearchResponse, StringsArray
from .SearchClient_config import base_url, endpoints


class SearchClient(Client):
    """APIs relating to Search and similar services"""

    def GetByQueryQuery(self, query: str) -> ResponseModel[SearchResponse] | ApiError:
        '''
        Search the site for occurrences of the query string. The maximum number of results returned is equal to the maximum page size of 100. To return subsequent pages, use the paginated overload.

  Query path: `/Search/`

  `ResponseModel.content` contains `models.SearchResponse` type.


  Parameters:
    `query`: str - The search query. Example: `Southwark`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_GetByQueryQuery'], endpoint_args={ 'query': query })

    def BusSchedulesByQueryQuery(self, query: str) -> ResponseModel[SearchResponse] | ApiError:
        '''
        Searches the bus schedules folder on S3 for a given bus number.

  Query path: `/Search/BusSchedules`

  `ResponseModel.content` contains `models.SearchResponse` type.


  Parameters:
    `query`: str - The search query. Example: `Southwark`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_BusSchedulesByQueryQuery'], endpoint_args={ 'query': query })

    def MetaSearchProviders(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available searchProvider names.

  Query path: `/Search/Meta/SearchProviders`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaSearchProviders'], endpoint_args=None)

    def MetaCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available search categories.

  Query path: `/Search/Meta/Categories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaCategories'], endpoint_args=None)

    def MetaSorts(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available sorting options.

  Query path: `/Search/Meta/Sorts`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaSorts'], endpoint_args=None)


class AsyncSearchClient(AsyncClient):
    """APIs relating to Search and similar services"""

    async def GetByQueryQuery(self, query: str) -> ResponseModel[SearchResponse] | ApiError:
        '''
        Search the site for occurrences of the query string. The maximum number of results returned is equal to the maximum page size of 100. To return subsequent pages, use the paginated overload.

  Query path: `/Search/`

  `ResponseModel.content` contains `models.SearchResponse` type.


  Parameters:
    `query`: str - The search query. Example: `Southwark`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Search_GetByQueryQuery'], endpoint_args={ 'query': query })

    async def BusSchedulesByQueryQuery(self, query: str) -> ResponseModel[SearchResponse] | ApiError:
        '''
        Searches the bus schedules folder on S3 for a given bus number.

  Query path: `/Search/BusSchedules`

  `ResponseModel.content` contains `models.SearchResponse` type.


  Parameters:
    `query`: str - The search query. Example: `Southwark`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Search_BusSchedulesByQueryQuery'], endpoint_args={ 'query': query })

    async def MetaSearchProviders(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available searchProvider names.

  Query path: `/Search/Meta/SearchProviders`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Search_MetaSearchProviders'], endpoint_args=None)

    async def MetaCategories(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available search categories.

  Query path: `/Search/Meta/Categories`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Search_MetaCategories'], endpoint_args=None)

    async def MetaSorts(self, ) -> ResponseModel[StringsArray] | ApiError:
        '''
        Gets the available sorting options.

  Query path: `/Search/Meta/Sorts`

  `ResponseModel.content` contains `models.StringsArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Search_MetaSorts'], endpoint_args=None)

