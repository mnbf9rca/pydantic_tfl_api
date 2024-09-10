from .JourneyClient_config import endpoints, base_url
from ..core import ApiError, ResponseModel, Client

class JourneyClient(Client):
    def Meta(self, ) -> ResponseModel | ApiError:
        '''
        Gets a list of all of the available journey planner modes

        ResponseModel.content contains `models.ModeArray` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Journey_Meta'], endpoint_args=None)

    def JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu(self, from_field: str, to: str, via: str | None = None, nationalSearch: bool | None = None, date: str | None = None, time: str | None = None, timeIs: str | None = None, journeyPreference: str | None = None, mode: list | None = None, accessibilityPreference: str | None = None, fromName: str | None = None, toName: str | None = None, viaName: str | None = None, maxTransferMinutes: str | None = None, maxWalkingMinutes: str | None = None, walkingSpeed: str | None = None, cyclePreference: str | None = None, adjustment: str | None = None, bikeProficiency: str | None = None, alternativeCycle: bool | None = None, alternativeWalking: bool | None = None, applyHtmlMarkup: bool | None = None, useMultiModalCall: bool | None = None, walkingOptimization: bool | None = None, taxiOnlyTrip: bool | None = None, routeBetweenEntrances: bool | None = None, useRealTimeLiveArrivals: bool | None = None, calcOneDirection: bool | None = None, includeAlternativeRoutes: bool | None = None, overrideMultiModalScenario: int | None = None, combineTransferLegs: bool | None = None) -> ResponseModel | ApiError:
        '''
        Perform a Journey Planner search from the parameters specified in simple types

        ResponseModel.content contains `models.ItineraryResult` type.

        Parameters:
        from_field: str - Origin of the journey. Can be WGS84 coordinates expressed as "lat,long", a UK postcode, a Naptan (StopPoint) id, an ICS StopId, or a free-text string (will cause disambiguation unless it exactly matches a point of interest name).. Example: 1001116
        to: str - Destination of the journey. Can be WGS84 coordinates expressed as "lat,long", a UK postcode, a Naptan (StopPoint) id, an ICS StopId, or a free-text string (will cause disambiguation unless it exactly matches a point of interest name).. Example: 1001949
        via: str - Travel through point on the journey. Can be WGS84 coordinates expressed as "lat,long", a UK postcode, a Naptan (StopPoint) id, an ICS StopId, or a free-text string (will cause disambiguation unless it exactly matches a point of interest name).. Example: None given
        nationalSearch: bool - Does the journey cover stops outside London? eg. "nationalSearch=true". Example: None given
        date: str - The date must be in yyyyMMdd format. Example: None given
        time: str - The time must be in HHmm format. Example: None given
        timeIs: str - Does the time given relate to arrival or leaving time? Possible options: "departing" | "arriving". Example: None given
        journeyPreference: str - The journey preference eg possible options: "leastinterchange" | "leasttime" | "leastwalking". Example: None given
        mode: list - The mode must be a comma separated list of modes. eg possible options: "public-bus,overground,train,tube,coach,dlr,cablecar,tram,river,walking,cycle". Example: None given
        accessibilityPreference: str - The accessibility preference must be a comma separated list eg. "noSolidStairs,noEscalators,noElevators,stepFreeToVehicle,stepFreeToPlatform". Example: NoRequirements
        fromName: str - An optional name to associate with the origin of the journey in the results.. Example: None given
        toName: str - An optional name to associate with the destination of the journey in the results.. Example: None given
        viaName: str - An optional name to associate with the via point of the journey in the results.. Example: None given
        maxTransferMinutes: str - The max walking time in minutes for transfer eg. "120". Example: None given
        maxWalkingMinutes: str - The max walking time in minutes for journeys eg. "120". Example: None given
        walkingSpeed: str - The walking speed. eg possible options: "slow" | "average" | "fast".. Example: Fast
        cyclePreference: str - The cycle preference. eg possible options: "allTheWay" | "leaveAtStation" | "takeOnTransport" | "cycleHire". Example: None given
        adjustment: str - Time adjustment command. eg possible options: "TripFirst" | "TripLast". Example: None given
        bikeProficiency: str - A comma separated list of cycling proficiency levels. eg possible options: "easy,moderate,fast". Example: None given
        alternativeCycle: bool - Option to determine whether to return alternative cycling journey. Example: None given
        alternativeWalking: bool - Option to determine whether to return alternative walking journey. Example: None given
        applyHtmlMarkup: bool - Flag to determine whether certain text (e.g. walking instructions) should be output with HTML tags or not.. Example: None given
        useMultiModalCall: bool - A boolean to indicate whether or not to return 3 public transport journeys, a bus journey, a cycle hire journey, a personal cycle journey and a walking journey. Example: None given
        walkingOptimization: bool - A boolean to indicate whether to optimize journeys using walking. Example: None given
        taxiOnlyTrip: bool - A boolean to indicate whether to return one or more taxi journeys. Note, setting this to true will override "useMultiModalCall".. Example: None given
        routeBetweenEntrances: bool - A boolean to indicate whether public transport routes should include directions between platforms and station entrances.. Example: None given
        useRealTimeLiveArrivals: bool - A boolean to indicate if we want to receive real time live arrivals data where available.. Example: None given
        calcOneDirection: bool - A boolean to make Journey Planner calculate journeys in one temporal direction only. In other words, only calculate journeys after the 'depart' time, or before the 'arrive' time. By default, the Journey Planner engine (EFA) calculates journeys in both temporal directions.. Example: None given
        includeAlternativeRoutes: bool - A boolean to make Journey Planner return alternative routes. Alternative routes are calculated by removing one or more lines included in the fastest route and re-calculating. By default, these journeys will not be returned.. Example: None given
        overrideMultiModalScenario: int - Format - int32. An optional integer to indicate what multi modal scenario we want to use.. Example: None given
        combineTransferLegs: bool - A boolean to indicate whether walking leg to station entrance and walking leg from station entrance to platform should be combined. Defaults to true. Example: None given
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Journey_JourneyResultsByPathFromPathToQueryViaQueryNationalSearchQueryDateQu'], params=[from_field, to], endpoint_args={ 'via': via, 'nationalSearch': nationalSearch, 'date': date, 'time': time, 'timeIs': timeIs, 'journeyPreference': journeyPreference, 'mode': mode, 'accessibilityPreference': accessibilityPreference, 'fromName': fromName, 'toName': toName, 'viaName': viaName, 'maxTransferMinutes': maxTransferMinutes, 'maxWalkingMinutes': maxWalkingMinutes, 'walkingSpeed': walkingSpeed, 'cyclePreference': cyclePreference, 'adjustment': adjustment, 'bikeProficiency': bikeProficiency, 'alternativeCycle': alternativeCycle, 'alternativeWalking': alternativeWalking, 'applyHtmlMarkup': applyHtmlMarkup, 'useMultiModalCall': useMultiModalCall, 'walkingOptimization': walkingOptimization, 'taxiOnlyTrip': taxiOnlyTrip, 'routeBetweenEntrances': routeBetweenEntrances, 'useRealTimeLiveArrivals': useRealTimeLiveArrivals, 'calcOneDirection': calcOneDirection, 'includeAlternativeRoutes': includeAlternativeRoutes, 'overrideMultiModalScenario': overrideMultiModalScenario, 'combineTransferLegs': combineTransferLegs })

    def Proxy(self, ) -> ResponseModel | ApiError:
        '''
        Forwards any remaining requests to the back-end

        ResponseModel.content contains `models.ObjectResponse` type.

        Parameters:
        No parameters required.
        '''
        return self._send_request_and_deserialize(base_url, endpoints['Forward_Proxy'], endpoint_args=None)

