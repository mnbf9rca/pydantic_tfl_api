from ..client import Client
from .AirQualityClient_config import endpoints
from .. import models
from ..models import ApiError

class AirQualityClient(Client):
    def get(self, ) -> models.LondonAirForecast | ApiError:
        '''
        Gets air quality data feed

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['AirQuality_Get'], endpoint_args=None)

