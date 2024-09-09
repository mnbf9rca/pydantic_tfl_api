from ..client import Client
from .SearchClient_config import endpoints
from .. import models
from ..models import ApiError

class SearchClient(Client):
    def getbyqueryquery(self, query: str) -> models.SearchResponse | ApiError:
        '''
        Search the site for occurrences of the query string. The maximum number of results returned is equal to the maximum page size of 100. To return subsequent pages, use the paginated overload.

        Parameters:
        query: str - The search query. Example: Southwark
        '''
        return self._send_request_and_deserialize(endpoints['Search_GetByQueryQuery'], endpoint_args={ 'query': query })

    def busschedulesbyqueryquery(self, query: str) -> models.SearchResponse | ApiError:
        '''
        Searches the bus schedules folder on S3 for a given bus number.

        Parameters:
        query: str - The search query. Example: Southwark
        '''
        return self._send_request_and_deserialize(endpoints['Search_BusSchedulesByQueryQuery'], endpoint_args={ 'query': query })

    def metasearchproviders(self, ) -> models.StringsArray | ApiError:
        '''
        Gets the available searchProvider names.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Search_MetaSearchProviders'], endpoint_args=None)

    def metacategories(self, ) -> models.StringsArray | ApiError:
        '''
        Gets the available search categories.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Search_MetaCategories'], endpoint_args=None)

    def metasorts(self, ) -> models.StringsArray | ApiError:
        '''
        Gets the available sorting options.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Search_MetaSorts'], endpoint_args=None)

