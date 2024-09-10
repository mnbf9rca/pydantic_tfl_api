from .SearchClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class SearchClient(Client):
    def getbyqueryquery(self, query: str) -> ResponseModel | ApiError:
        '''
        Search the site for occurrences of the query string. The maximum number of results returned is equal to the maximum page size of 100. To return subsequent pages, use the paginated overload.

        ResponseModel.content contains `models.SearchResponse` type.

        Parameters:
        query: str - The search query. Example: Southwark
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_GetByQueryQuery'], endpoint_args={ 'query': query })

    def busschedulesbyqueryquery(self, query: str) -> ResponseModel | ApiError:
        '''
        Searches the bus schedules folder on S3 for a given bus number.

        ResponseModel.content contains `models.SearchResponse` type.

        Parameters:
        query: str - The search query. Example: Southwark
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_BusSchedulesByQueryQuery'], endpoint_args={ 'query': query })

    def metasearchproviders(self, ) -> ResponseModel | ApiError:
        '''
        Gets the available searchProvider names.

        ResponseModel.content contains `models.StringsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaSearchProviders'], endpoint_args=None)

    def metacategories(self, ) -> ResponseModel | ApiError:
        '''
        Gets the available search categories.

        ResponseModel.content contains `models.StringsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaCategories'], endpoint_args=None)

    def metasorts(self, ) -> ResponseModel | ApiError:
        '''
        Gets the available sorting options.

        ResponseModel.content contains `models.StringsArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Search_MetaSorts'], endpoint_args=None)

