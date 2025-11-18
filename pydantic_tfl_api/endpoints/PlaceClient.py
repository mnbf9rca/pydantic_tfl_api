from ..core import ApiError, AsyncClient, Client, ResponseModel
from ..models import (
    Object,
    ObjectResponse,
    PlaceArray,
    PlaceCategoryArray,
    StopPointArray,
)
from .PlaceClient_config import base_url, endpoints


class PlaceClient(Client):
    """APIs relating to Place and similar services"""

    def MetaCategories(self, ) -> ResponseModel[PlaceCategoryArray] | ApiError:
        '''
        Gets a list of all of the available place property categories and keys.

  Query path: `/Place/Meta/Categories`

  `ResponseModel.content` contains `models.PlaceCategoryArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_MetaCategories'], endpoint_args=None)

    def MetaPlaceTypes(self, ) -> ResponseModel[PlaceCategoryArray] | ApiError:
        '''
        Gets a list of the available types of Place.

  Query path: `/Place/Meta/PlaceTypes`

  `ResponseModel.content` contains `models.PlaceCategoryArray` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_MetaPlaceTypes'], endpoint_args=None)

    def GetByTypeByPathTypesQueryActiveOnly(self, types: str, activeOnly: bool | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all places of a given type

  Query path: `/Place/Type/{types}`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `types`: str - A comma-separated list of the types to return. Max. approx 12 types. A valid list of place types can be obtained from the /Place/Meta/placeTypes endpoint.. Example: `CarPark`
    `activeOnly`: bool - An optional parameter to limit the results to active records only (Currently only the 'VariableMessageSign' place type is supported).
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_GetByTypeByPathTypesQueryActiveOnly'], params=[types], endpoint_args={ 'activeOnly': activeOnly })

    def GetByPathIdQueryIncludeChildren(self, id: str, includeChildren: bool | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets the place with the given id.

  Query path: `/Place/{id}`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `id`: str - The id of the place, you can use the /Place/Types/{types} endpoint to get a list of places for a given type including their ids. Example: `CarParks_800491`
    `includeChildren`: bool - Defaults to false. If true child places e.g. individual charging stations at a charge point while be included, otherwise just the URLs of any child places will be returned.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_GetByPathIdQueryIncludeChildren'], params=[id], endpoint_args={ 'includeChildren': includeChildren })

    def GetByGeoPointByQueryLatQueryLonQueryRadiusQueryCategoriesQueryIncludeC(self, Lat: float, Lon: float, radius: float | None = None, categories: list | None = None, includeChildren: bool | None = None, type: list | None = None, activeOnly: bool | None = None, numberOfPlacesToReturn: int | None = None) -> ResponseModel[StopPointArray] | ApiError:
        '''
        Gets the places that lie within a geographic region. The geographic region of interest can either be specified by using a lat/lon geo-point and a radius in metres to return places within the locus defined by the lat/lon of its centre or alternatively, by the use of a bounding box defined by the lat/lon of its north-west and south-east corners. Optionally filters on type and can strip properties for a smaller payload.

  Query path: `/Place/`

  `ResponseModel.content` contains `models.StopPointArray` type.


  Parameters:
    `Lat`: float - Format - double. lat is latitude of the centre of the bounding circle.. Example: `51.5029703`
    `Lon`: float - Format - double. lon is longitude of the centre of the bounding circle.. Example: `-0.1365283`
    `radius`: float - Format - double. The radius of the bounding circle in metres when only lat/lon are specified.. Example: `100`
    `categories`: list - An optional list of comma separated property categories to return in the Place's property bag. If null or empty, all categories of property are returned. Pass the keyword "none" to return no properties (a valid list of categories can be obtained from the /Place/Meta/categories endpoint).
    `includeChildren`: bool - Defaults to false. If true child places e.g. individual charging stations at a charge point while be included, otherwise just the URLs of any child places will be returned.
    `type`: list - Place types to filter on, or null to return all types.
    `activeOnly`: bool - An optional parameter to limit the results to active records only (Currently only the 'VariableMessageSign' place type is supported).
    `numberOfPlacesToReturn`: int - Format - int32. If specified, limits the number of returned places equal to the given value.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_GetByGeoPointByQueryLatQueryLonQueryRadiusQueryCategoriesQueryIncludeC'], endpoint_args={ 'Lat': Lat, 'Lon': Lon, 'radius': radius, 'categories': categories, 'includeChildren': includeChildren, 'type': type, 'activeOnly': activeOnly, 'numberOfPlacesToReturn': numberOfPlacesToReturn })

    def GetAtByPathTypePathLatPathLon(self, type: str, lat: float, lon: float) -> ResponseModel[Object] | ApiError:
        '''
        Gets any places of the given type whose geography intersects the given latitude and longitude. In practice this means the Place must be polygonal e.g. a BoroughBoundary.

  Query path: `/Place/{type}/At/{lat}/{lon}`

  `ResponseModel.content` contains `models.Object` type.


  Parameters:
    `type`: str - The place type (a valid list of place types can be obtained from the /Place/Meta/placeTypes endpoint). Example: `CarPark`
    `lat`: float - Format - double. lat is latitude of the centre of the bounding circle.. Example: `51.5029703`
    `lon`: float - Format - double. lon is longitude of the centre of the bounding circle. Example: `-0.1365283`
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_GetAtByPathTypePathLatPathLon'], params=[type, lat, lon], endpoint_args=None)

    def SearchByQueryNameQueryTypes(self, name: str, types: list | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all places that matches the given query

  Query path: `/Place/Search`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `name`: str - The name of the place, you can use the /Place/Types/{types} endpoint to get a list of places for a given type including their names.. Example: `Bridge`
    `types`: list - A comma-separated list of the types to return. Max. approx 12 types..
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Place_SearchByQueryNameQueryTypes'], endpoint_args={ 'name': name, 'types': types })

    def Proxy(self, ) -> ResponseModel[ObjectResponse] | ApiError:
        '''
        Forwards any remaining requests to the back-end

  Query path: `/Place/*`

  `ResponseModel.content` contains `models.ObjectResponse` type.


  Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)


class AsyncPlaceClient(AsyncClient):
    """APIs relating to Place and similar services"""

    async def MetaCategories(self, ) -> ResponseModel[PlaceCategoryArray] | ApiError:
        '''
        Gets a list of all of the available place property categories and keys.

  Query path: `/Place/Meta/Categories`

  `ResponseModel.content` contains `models.PlaceCategoryArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_MetaCategories'], endpoint_args=None)

    async def MetaPlaceTypes(self, ) -> ResponseModel[PlaceCategoryArray] | ApiError:
        '''
        Gets a list of the available types of Place.

  Query path: `/Place/Meta/PlaceTypes`

  `ResponseModel.content` contains `models.PlaceCategoryArray` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_MetaPlaceTypes'], endpoint_args=None)

    async def GetByTypeByPathTypesQueryActiveOnly(self, types: str, activeOnly: bool | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all places of a given type

  Query path: `/Place/Type/{types}`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `types`: str - A comma-separated list of the types to return. Max. approx 12 types. A valid list of place types can be obtained from the /Place/Meta/placeTypes endpoint.. Example: `CarPark`
    `activeOnly`: bool - An optional parameter to limit the results to active records only (Currently only the 'VariableMessageSign' place type is supported).
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_GetByTypeByPathTypesQueryActiveOnly'], params=[types], endpoint_args={ 'activeOnly': activeOnly })

    async def GetByPathIdQueryIncludeChildren(self, id: str, includeChildren: bool | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets the place with the given id.

  Query path: `/Place/{id}`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `id`: str - The id of the place, you can use the /Place/Types/{types} endpoint to get a list of places for a given type including their ids. Example: `CarParks_800491`
    `includeChildren`: bool - Defaults to false. If true child places e.g. individual charging stations at a charge point while be included, otherwise just the URLs of any child places will be returned.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_GetByPathIdQueryIncludeChildren'], params=[id], endpoint_args={ 'includeChildren': includeChildren })

    async def GetByGeoPointByQueryLatQueryLonQueryRadiusQueryCategoriesQueryIncludeC(self, Lat: float, Lon: float, radius: float | None = None, categories: list | None = None, includeChildren: bool | None = None, type: list | None = None, activeOnly: bool | None = None, numberOfPlacesToReturn: int | None = None) -> ResponseModel[StopPointArray] | ApiError:
        '''
        Gets the places that lie within a geographic region. The geographic region of interest can either be specified by using a lat/lon geo-point and a radius in metres to return places within the locus defined by the lat/lon of its centre or alternatively, by the use of a bounding box defined by the lat/lon of its north-west and south-east corners. Optionally filters on type and can strip properties for a smaller payload.

  Query path: `/Place/`

  `ResponseModel.content` contains `models.StopPointArray` type.


  Parameters:
    `Lat`: float - Format - double. lat is latitude of the centre of the bounding circle.. Example: `51.5029703`
    `Lon`: float - Format - double. lon is longitude of the centre of the bounding circle.. Example: `-0.1365283`
    `radius`: float - Format - double. The radius of the bounding circle in metres when only lat/lon are specified.. Example: `100`
    `categories`: list - An optional list of comma separated property categories to return in the Place's property bag. If null or empty, all categories of property are returned. Pass the keyword "none" to return no properties (a valid list of categories can be obtained from the /Place/Meta/categories endpoint).
    `includeChildren`: bool - Defaults to false. If true child places e.g. individual charging stations at a charge point while be included, otherwise just the URLs of any child places will be returned.
    `type`: list - Place types to filter on, or null to return all types.
    `activeOnly`: bool - An optional parameter to limit the results to active records only (Currently only the 'VariableMessageSign' place type is supported).
    `numberOfPlacesToReturn`: int - Format - int32. If specified, limits the number of returned places equal to the given value.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_GetByGeoPointByQueryLatQueryLonQueryRadiusQueryCategoriesQueryIncludeC'], endpoint_args={ 'Lat': Lat, 'Lon': Lon, 'radius': radius, 'categories': categories, 'includeChildren': includeChildren, 'type': type, 'activeOnly': activeOnly, 'numberOfPlacesToReturn': numberOfPlacesToReturn })

    async def GetAtByPathTypePathLatPathLon(self, type: str, lat: float, lon: float) -> ResponseModel[Object] | ApiError:
        '''
        Gets any places of the given type whose geography intersects the given latitude and longitude. In practice this means the Place must be polygonal e.g. a BoroughBoundary.

  Query path: `/Place/{type}/At/{lat}/{lon}`

  `ResponseModel.content` contains `models.Object` type.


  Parameters:
    `type`: str - The place type (a valid list of place types can be obtained from the /Place/Meta/placeTypes endpoint). Example: `CarPark`
    `lat`: float - Format - double. lat is latitude of the centre of the bounding circle.. Example: `51.5029703`
    `lon`: float - Format - double. lon is longitude of the centre of the bounding circle. Example: `-0.1365283`
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_GetAtByPathTypePathLatPathLon'], params=[type, lat, lon], endpoint_args=None)

    async def SearchByQueryNameQueryTypes(self, name: str, types: list | None = None) -> ResponseModel[PlaceArray] | ApiError:
        '''
        Gets all places that matches the given query

  Query path: `/Place/Search`

  `ResponseModel.content` contains `models.PlaceArray` type.


  Parameters:
    `name`: str - The name of the place, you can use the /Place/Types/{types} endpoint to get a list of places for a given type including their names.. Example: `Bridge`
    `types`: list - A comma-separated list of the types to return. Max. approx 12 types..
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Place_SearchByQueryNameQueryTypes'], endpoint_args={ 'name': name, 'types': types })

    async def Proxy(self, ) -> ResponseModel[ObjectResponse] | ApiError:
        '''
        Forwards any remaining requests to the back-end

  Query path: `/Place/*`

  `ResponseModel.content` contains `models.ObjectResponse` type.


  Parameters:
        No parameters required.
        '''
        return await self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)

