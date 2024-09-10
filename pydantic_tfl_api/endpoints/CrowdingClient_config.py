base_url = "https://api.tfl.gov.uk"
endpoints = {
    'naptan': {'uri': '/crowding/{0}', 'model': 'GenericResponseModel'},
    'dayofweek': {'uri': '/crowding/{0}/{1}', 'model': 'GenericResponseModel'},
    'live': {'uri': '/crowding/{0}/Live', 'model': 'GenericResponseModel'},
}
