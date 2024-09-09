from ..client import Client
from .OccupancyClient_config import endpoints
from .. import models
from ..models import ApiError

class OccupancyClient(Client):
    def getallchargeconnectorstatus(self, ) -> models.ChargeConnectorOccupancyArray | ApiError:
        '''
        Gets the occupancy for all charge connectors

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Occupancy_GetAllChargeConnectorStatus'], endpoint_args=None)

    def getchargeconnectorstatusbypathids(self, ids: str) -> models.ChargeConnectorOccupancyArray | ApiError:
        '''
        Gets the occupancy for a charge connectors with a given id (sourceSystemPlaceId)

        Parameters:
        ids: str - . Example: ChargePointCM-24473-67148
        '''
        return self._send_request_and_deserialize(endpoints['Occupancy_GetChargeConnectorStatusByPathIds'], params=[ids], endpoint_args=None)

    def getbikepointsoccupanciesbypathids(self, ids: str) -> models.BikePointOccupancyArray | ApiError:
        '''
        Get the occupancy for bike points.

        Parameters:
        ids: str - . Example: BikePoints_805
        '''
        return self._send_request_and_deserialize(endpoints['Occupancy_GetBikePointsOccupanciesByPathIds'], params=[ids], endpoint_args=None)

    def proxy(self, ) -> models.GenericResponseModel | ApiError:
        '''
        Forwards any remaining requests to the back-end

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(endpoints['Forward_Proxy'], endpoint_args=None)

