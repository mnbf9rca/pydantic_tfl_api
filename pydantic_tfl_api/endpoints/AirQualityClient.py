from .AirQualityClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class AirQualityClient(Client):
    def get(self, ) -> ResponseModel | ApiError:
        '''
        Gets air quality data feed

        ResponseModel.content contains `models.LondonAirForecast` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['AirQuality_Get'], endpoint_args=None)

