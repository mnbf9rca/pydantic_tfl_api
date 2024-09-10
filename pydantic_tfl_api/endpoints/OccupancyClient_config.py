base_url = "https://api.tfl.gov.uk"
endpoints = {
    'Occupancy_GetAllChargeConnectorStatus': {'uri': '/Occupancy/ChargeConnector', 'model': 'ChargeConnectorOccupancyArray'},
    'Occupancy_GetChargeConnectorStatusByPathIds': {'uri': '/Occupancy/ChargeConnector/{0}', 'model': 'ChargeConnectorOccupancyArray'},
    'Occupancy_GetBikePointsOccupanciesByPathIds': {'uri': '/Occupancy/BikePoints/{0}', 'model': 'BikePointOccupancyArray'},
    'Forward_Proxy': {'uri': '/Occupancy/*', 'model': 'GenericResponseModel'},
}
