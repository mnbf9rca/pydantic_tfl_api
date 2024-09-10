from .OccupancyClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client
from ..models import BikePointOccupancyArray, ChargeConnectorOccupancyArray, GenericResponseModel

class OccupancyClient(Client):
    def GetAllChargeConnectorStatus(self, ) -> ResponseModel[ChargeConnectorOccupancyArray] | ApiError:
        '''
        Gets the occupancy for all charge connectors

  Query path: `/Occupancy/ChargeConnector`

  `ResponseModel.content` contains `models.ChargeConnectorOccupancyArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Occupancy_GetAllChargeConnectorStatus'], endpoint_args=None)

    def GetChargeConnectorStatusByPathIds(self, ids: str) -> ResponseModel[ChargeConnectorOccupancyArray] | ApiError:
        '''
        Gets the occupancy for a charge connectors with a given id (sourceSystemPlaceId)

  Query path: `/Occupancy/ChargeConnector/{ids}`

  `ResponseModel.content` contains `models.ChargeConnectorOccupancyArray` type.


  Parameters:
    `ids`: str - . Example: `ChargePointCM-24473-67148`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Occupancy_GetChargeConnectorStatusByPathIds'], params=[ids], endpoint_args=None)

    def GetBikePointsOccupanciesByPathIds(self, ids: str) -> ResponseModel[BikePointOccupancyArray] | ApiError:
        '''
        Get the occupancy for bike points.

  Query path: `/Occupancy/BikePoints/{ids}`

  `ResponseModel.content` contains `models.BikePointOccupancyArray` type.


  Parameters:
    `ids`: str - . Example: `BikePoints_805`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Occupancy_GetBikePointsOccupanciesByPathIds'], params=[ids], endpoint_args=None)

    def Proxy(self, ) -> ResponseModel[GenericResponseModel] | ApiError:
        '''
        Forwards any remaining requests to the back-end

  Query path: `/Occupancy/*`

  `ResponseModel.content` contains `models.GenericResponseModel` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)

