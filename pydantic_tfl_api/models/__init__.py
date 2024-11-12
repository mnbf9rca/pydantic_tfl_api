from typing import Literal
from .AccidentDetailArray import AccidentDetailArray
from .AccidentDetail import AccidentDetail
from .ActiveServiceTypesArray import ActiveServiceTypesArray
from .ActiveServiceType import ActiveServiceType
from .ArrivalDepartureArray import ArrivalDepartureArray
from .ArrivalDeparture import ArrivalDeparture
from .BikePointOccupancyArray import BikePointOccupancyArray
from .BikePointOccupancy import BikePointOccupancy
from .CarParkOccupancy import CarParkOccupancy
from .Bay import Bay
from .Casualty import Casualty
from .ChargeConnectorOccupancyArray import ChargeConnectorOccupancyArray
from .ChargeConnectorOccupancy import ChargeConnectorOccupancy
from .DisruptedPointArray import DisruptedPointArray
from .DisruptedPoint import DisruptedPoint
from .DisruptionArray import DisruptionArray
from .GenericResponseModel import GenericResponseModel
from .ItineraryResult import ItineraryResult
from .Journey import Journey
from .JourneyFare import JourneyFare
from .Fare import Fare
from .FareCaveat import FareCaveat
from .FareTap import FareTap
from .FareTapDetails import FareTapDetails
from .JourneyPlannerCycleHireDockingStationData import JourneyPlannerCycleHireDockingStationData
from .JourneyVector import JourneyVector
from .Leg import Leg
from .Instruction import Instruction
from .InstructionStep import InstructionStep
from .LiftDisruptionsArray import LiftDisruptionsArray
from .LiftDisruption import LiftDisruption
from .LineArray import LineArray
from .Line import Line
from .LineServiceTypeArray import LineServiceTypeArray
from .LineServiceType import LineServiceType
from .LineSpecificServiceType import LineSpecificServiceType
from .LineServiceTypeInfo import LineServiceTypeInfo
from .LineStatus import LineStatus
from .Disruption import Disruption
from .LondonAirForecast import LondonAirForecast
from .MatchedRoute import MatchedRoute
from .ModeArray import ModeArray
from .Mode import Mode
from .Object import Object
from .ObjectResponse import ObjectResponse
from .Obstacle import Obstacle
from .Path import Path
from .JpElevation import JpElevation
from .PathAttribute import PathAttribute
from .PlaceArray import PlaceArray
from .PlaceCategoryArray import PlaceCategoryArray
from .PlannedWork import PlannedWork
from .Point import Point
from .PredictionArray import PredictionArray
from .Prediction import Prediction
from .PredictionTiming import PredictionTiming
from .RoadCorridorsArray import RoadCorridorsArray
from .RoadCorridor import RoadCorridor
from .RoadDisruptionsArray import RoadDisruptionsArray
from .RoadDisruption import RoadDisruption
from .RoadDisruptionImpactArea import RoadDisruptionImpactArea
from .RoadDisruptionLine import RoadDisruptionLine
from .DbGeography import DbGeography
from .DbGeographyWellKnownValue import DbGeographyWellKnownValue
from .RoadDisruptionSchedule import RoadDisruptionSchedule
from .RoadProject import RoadProject
from .RouteOption import RouteOption
from .RouteSearchResponse import RouteSearchResponse
from .RouteSearchMatch import RouteSearchMatch
from .LineRouteSection import LineRouteSection
from .MatchedRouteSections import MatchedRouteSections
from .RouteSection import RouteSection
from .RouteSectionNaptanEntrySequence import RouteSectionNaptanEntrySequence
from .RouteSequence import RouteSequence
from .OrderedRoute import OrderedRoute
from .SearchCriteria import SearchCriteria
from .SearchResponse import SearchResponse
from .SearchMatch import SearchMatch
from .StatusSeveritiesArray import StatusSeveritiesArray
from .StatusSeverity import StatusSeverity
from .StopPointArray import StopPointArray
from .StopPointCategoryArray import StopPointCategoryArray
from .PlaceCategory import PlaceCategory
from .StopPointRouteSectionArray import StopPointRouteSectionArray
from .StopPointRouteSection import StopPointRouteSection
from .StopPointSequence import StopPointSequence
from .StopPointsResponse import StopPointsResponse
from .StopPoint import StopPoint
from .LineGroup import LineGroup
from .LineModeGroup import LineModeGroup
from .Street import Street
from .StreetSegment import StreetSegment
from .StringsArray import StringsArray
from .TimeAdjustments import TimeAdjustments
from .TimeAdjustment import TimeAdjustment
from .TimetableResponse import TimetableResponse
from .Disambiguation import Disambiguation
from .DisambiguationOption import DisambiguationOption
from .MatchedStop import MatchedStop
from .Identifier import Identifier
from .Crowding import Crowding
from .PassengerFlow import PassengerFlow
from .Timetable import Timetable
from .TimetableRoute import TimetableRoute
from .Schedule import Schedule
from .KnownJourney import KnownJourney
from .Period import Period
from .ServiceFrequency import ServiceFrequency
from .StationInterval import StationInterval
from .Interval import Interval
from .TrainLoading import TrainLoading
from .TwentyFourHourClockTime import TwentyFourHourClockTime
from .ValidityPeriod import ValidityPeriod
from .Vehicle import Vehicle
from .VehicleMatch import VehicleMatch
from .AdditionalProperties import AdditionalProperties
from .Place import Place

ResponseModelName = Literal[
    "AccidentDetailArray",
    "AccidentDetail",
    "ActiveServiceTypesArray",
    "ActiveServiceType",
    "ArrivalDepartureArray",
    "ArrivalDeparture",
    "BikePointOccupancyArray",
    "BikePointOccupancy",
    "CarParkOccupancy",
    "Bay",
    "Casualty",
    "ChargeConnectorOccupancyArray",
    "ChargeConnectorOccupancy",
    "DisruptedPointArray",
    "DisruptedPoint",
    "DisruptionArray",
    "GenericResponseModel",
    "ItineraryResult",
    "Journey",
    "JourneyFare",
    "Fare",
    "FareCaveat",
    "FareTap",
    "FareTapDetails",
    "JourneyPlannerCycleHireDockingStationData",
    "JourneyVector",
    "Leg",
    "Instruction",
    "InstructionStep",
    "LiftDisruptionsArray",
    "LiftDisruption",
    "LineArray",
    "Line",
    "LineServiceTypeArray",
    "LineServiceType",
    "LineSpecificServiceType",
    "LineServiceTypeInfo",
    "LineStatus",
    "Disruption",
    "LondonAirForecast",
    "MatchedRoute",
    "ModeArray",
    "Mode",
    "Object",
    "ObjectResponse",
    "Obstacle",
    "Path",
    "JpElevation",
    "PathAttribute",
    "PlaceArray",
    "PlaceCategoryArray",
    "PlannedWork",
    "Point",
    "PredictionArray",
    "Prediction",
    "PredictionTiming",
    "RoadCorridorsArray",
    "RoadCorridor",
    "RoadDisruptionsArray",
    "RoadDisruption",
    "RoadDisruptionImpactArea",
    "RoadDisruptionLine",
    "DbGeography",
    "DbGeographyWellKnownValue",
    "RoadDisruptionSchedule",
    "RoadProject",
    "RouteOption",
    "RouteSearchResponse",
    "RouteSearchMatch",
    "LineRouteSection",
    "MatchedRouteSections",
    "RouteSection",
    "RouteSectionNaptanEntrySequence",
    "RouteSequence",
    "OrderedRoute",
    "SearchCriteria",
    "SearchResponse",
    "SearchMatch",
    "StatusSeveritiesArray",
    "StatusSeverity",
    "StopPointArray",
    "StopPointCategoryArray",
    "PlaceCategory",
    "StopPointRouteSectionArray",
    "StopPointRouteSection",
    "StopPointSequence",
    "StopPointsResponse",
    "StopPoint",
    "LineGroup",
    "LineModeGroup",
    "Street",
    "StreetSegment",
    "StringsArray",
    "TimeAdjustments",
    "TimeAdjustment",
    "TimetableResponse",
    "Disambiguation",
    "DisambiguationOption",
    "MatchedStop",
    "Identifier",
    "Crowding",
    "PassengerFlow",
    "Timetable",
    "TimetableRoute",
    "Schedule",
    "KnownJourney",
    "Period",
    "ServiceFrequency",
    "StationInterval",
    "Interval",
    "TrainLoading",
    "TwentyFourHourClockTime",
    "ValidityPeriod",
    "Vehicle",
    "VehicleMatch",
    "AdditionalProperties",
    "Place"
]

__all__ = [
    "AccidentDetailArray",
    "AccidentDetail",
    "ActiveServiceTypesArray",
    "ActiveServiceType",
    "ArrivalDepartureArray",
    "ArrivalDeparture",
    "BikePointOccupancyArray",
    "BikePointOccupancy",
    "CarParkOccupancy",
    "Bay",
    "Casualty",
    "ChargeConnectorOccupancyArray",
    "ChargeConnectorOccupancy",
    "DisruptedPointArray",
    "DisruptedPoint",
    "DisruptionArray",
    "GenericResponseModel",
    "ItineraryResult",
    "Journey",
    "JourneyFare",
    "Fare",
    "FareCaveat",
    "FareTap",
    "FareTapDetails",
    "JourneyPlannerCycleHireDockingStationData",
    "JourneyVector",
    "Leg",
    "Instruction",
    "InstructionStep",
    "LiftDisruptionsArray",
    "LiftDisruption",
    "LineArray",
    "Line",
    "LineServiceTypeArray",
    "LineServiceType",
    "LineSpecificServiceType",
    "LineServiceTypeInfo",
    "LineStatus",
    "Disruption",
    "LondonAirForecast",
    "MatchedRoute",
    "ModeArray",
    "Mode",
    "Object",
    "ObjectResponse",
    "Obstacle",
    "Path",
    "JpElevation",
    "PathAttribute",
    "PlaceArray",
    "PlaceCategoryArray",
    "PlannedWork",
    "Point",
    "PredictionArray",
    "Prediction",
    "PredictionTiming",
    "RoadCorridorsArray",
    "RoadCorridor",
    "RoadDisruptionsArray",
    "RoadDisruption",
    "RoadDisruptionImpactArea",
    "RoadDisruptionLine",
    "DbGeography",
    "DbGeographyWellKnownValue",
    "RoadDisruptionSchedule",
    "RoadProject",
    "RouteOption",
    "RouteSearchResponse",
    "RouteSearchMatch",
    "LineRouteSection",
    "MatchedRouteSections",
    "RouteSection",
    "RouteSectionNaptanEntrySequence",
    "RouteSequence",
    "OrderedRoute",
    "SearchCriteria",
    "SearchResponse",
    "SearchMatch",
    "StatusSeveritiesArray",
    "StatusSeverity",
    "StopPointArray",
    "StopPointCategoryArray",
    "PlaceCategory",
    "StopPointRouteSectionArray",
    "StopPointRouteSection",
    "StopPointSequence",
    "StopPointsResponse",
    "StopPoint",
    "LineGroup",
    "LineModeGroup",
    "Street",
    "StreetSegment",
    "StringsArray",
    "TimeAdjustments",
    "TimeAdjustment",
    "TimetableResponse",
    "Disambiguation",
    "DisambiguationOption",
    "MatchedStop",
    "Identifier",
    "Crowding",
    "PassengerFlow",
    "Timetable",
    "TimetableRoute",
    "Schedule",
    "KnownJourney",
    "Period",
    "ServiceFrequency",
    "StationInterval",
    "Interval",
    "TrainLoading",
    "TwentyFourHourClockTime",
    "ValidityPeriod",
    "Vehicle",
    "VehicleMatch",
    "AdditionalProperties",
    "Place"
]
