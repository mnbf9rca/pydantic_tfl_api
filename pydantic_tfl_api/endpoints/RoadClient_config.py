base_url = "https://api.tfl.gov.uk"
endpoints = {
    'Road_Get': {'uri': '/Road/', 'model': 'RoadCorridorsArray'},
    'Road_GetByPathIds': {'uri': '/Road/{0}', 'model': 'RoadCorridorsArray'},
    'Road_StatusByPathIdsQueryStartDateQueryEndDate': {'uri': '/Road/{0}/Status', 'model': 'RoadCorridorsArray'},
    'Road_DisruptionByPathIdsQueryStripContentQuerySeveritiesQueryCategoriesQuery': {'uri': '/Road/{0}/Disruption', 'model': 'RoadDisruptionsArray'},
    'Road_DisruptedStreetsByQueryStartDateQueryEndDate': {'uri': '/Road/all/Street/Disruption', 'model': 'Object'},
    'Road_DisruptionByIdByPathDisruptionIdsQueryStripContent': {'uri': '/Road/all/Disruption/{0}', 'model': 'RoadDisruption'},
    'Road_MetaCategories': {'uri': '/Road/Meta/Categories', 'model': 'StringsArray'},
    'Road_MetaSeverities': {'uri': '/Road/Meta/Severities', 'model': 'StatusSeveritiesArray'},
}
