base_url = "https://api.tfl.gov.uk"
endpoints = {
    'Journey_Meta': {'uri': '/Journey/Meta/Modes', 'model': 'ModeArray'},
    'Journey_JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu': {'uri': '/Journey/JourneyResults/{0}/to/{1}', 'model': 'ItineraryResult'},
    'Forward_Proxy': {'uri': '/Journey/*', 'model': 'ObjectResponse'},
}
