base_url = "https://api.tfl.gov.uk"
endpoints = {
    'Search_GetByQueryQuery': {'uri': '/Search/', 'model': 'SearchResponse'},
    'Search_BusSchedulesByQueryQuery': {'uri': '/Search/BusSchedules', 'model': 'SearchResponse'},
    'Search_MetaSearchProviders': {'uri': '/Search/Meta/SearchProviders', 'model': 'StringsArray'},
    'Search_MetaCategories': {'uri': '/Search/Meta/Categories', 'model': 'StringsArray'},
    'Search_MetaSorts': {'uri': '/Search/Meta/Sorts', 'model': 'StringsArray'},
}
