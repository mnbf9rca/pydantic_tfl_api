base_url = "https://api.tfl.gov.uk"
endpoints = {
    'BikePoint_GetAll': {'uri': '/BikePoint/', 'model': 'PlaceArray'},
    'BikePoint_Get': {'uri': '/BikePoint/{0}', 'model': 'Place'},
    'BikePoint_Search': {'uri': '/BikePoint/Search', 'model': 'PlaceArray'},
}
