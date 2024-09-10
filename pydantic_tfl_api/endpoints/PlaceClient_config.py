base_url = "https://api.tfl.gov.uk"
endpoints = {
    'Place_MetaCategories': {'uri': '/Place/Meta/Categories', 'model': 'PlaceCategoryArray'},
    'Place_MetaPlaceTypes': {'uri': '/Place/Meta/PlaceTypes', 'model': 'PlaceCategoryArray'},
    'Place_GetByTypeByPathTypesQueryActiveOnly': {'uri': '/Place/Type/{0}', 'model': 'PlaceArray'},
    'Place_GetByPathIdQueryIncludeChildren': {'uri': '/Place/{0}', 'model': 'PlaceArray'},
    'Place_GetByGeoPointByQueryLatQueryLonQueryRadiusQueryCategoriesQueryIncludeC': {'uri': '/Place/', 'model': 'StopPointArray'},
    'Place_GetAtByPathTypePathLatPathLon': {'uri': '/Place/{0}/At/{1}/{2}', 'model': 'Object'},
    'Place_SearchByQueryNameQueryTypes': {'uri': '/Place/Search', 'model': 'PlaceArray'},
    'Forward_Proxy': {'uri': '/Place/*', 'model': 'ObjectResponse'},
}
