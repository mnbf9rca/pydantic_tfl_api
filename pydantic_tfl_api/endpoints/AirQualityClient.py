from ..core import ApiError, Client, ResponseModel
from ..models import LondonAirForecast
from .AirQualityClient_config import base_url, endpoints


class AirQualityClient(Client):
    """APIs relating to AirQuality and similar services"""

    def Get(self, ) -> ResponseModel[LondonAirForecast] | ApiError:
        '''
        Gets air quality data feed

  Query path: `/AirQuality/`

  `ResponseModel.content` contains `models.LondonAirForecast` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AirQuality_Get'], endpoint_args=None)

