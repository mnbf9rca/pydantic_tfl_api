from .AirQualityClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import LondonAirForecast

class AirQualityClient(Client):
    def Get(self, ) -> ResponseModel[LondonAirForecast] | ApiError:
        '''
        Gets air quality data feed

  Query path: `/AirQuality/`

  `ResponseModel.content` contains `models.LondonAirForecast` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AirQuality_Get'], endpoint_args=None)

