from ..client import Client
from .BikePointClient_config import endpoints
from .. import models
from ..models import ApiError

class BikePointClient(Client):
    def getall(self, ) -> models.PlaceArray | ApiError:
        '''
        Gets all bike point locations. The Place object has an addtionalProperties array which contains the nbBikes, nbDocks and nbSpaces
            numbers which give the status of the BikePoint. A mismatch in these numbers i.e. nbDocks - (nbBikes + nbSpaces) != 0 indicates broken docks.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['BikePoint_GetAll'], endpoint_args=None)

    def get(self, id: str) -> models.Place | ApiError:
        '''
        Gets the bike point with the given id.

        Parameters:
        id: str - A bike point id (a list of ids can be obtained from the above BikePoint call). Example: BikePoints_583
        '''
        return self._send_request_and_deserialize(endpoints['BikePoint_Get'], params=[id], endpoint_args=None)

    def search(self, query: str) -> models.PlaceArray | ApiError:
        '''
        Search for bike stations by their name, a bike point's name often contains information about the name of the street
            or nearby landmarks, for example. Note that the search result does not contain the PlaceProperties i.e. the status
            or occupancy of the BikePoint, to get that information you should retrieve the BikePoint by its id on /BikePoint/id.

        Parameters:
        query: str - The search term e.g. "St. James". Example: London
        '''
        return self._send_request_and_deserialize(endpoints['BikePoint_Search'], endpoint_args={ 'query': query })

