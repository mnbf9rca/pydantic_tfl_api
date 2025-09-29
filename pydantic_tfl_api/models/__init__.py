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
from .PlaceCategory import PlaceCategory
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
from ..core.package_models import GenericResponseModel
from typing import Literal

ResponseModelName = Literal[
    "AccidentDetail",
    "AccidentDetailArray",
    "ActiveServiceType",
    "ActiveServiceTypesArray",
    "AdditionalProperties",
    "ArrivalDeparture",
    "ArrivalDepartureArray",
    "Bay",
    "BikePointOccupancy",
    "BikePointOccupancyArray",
    "CarParkOccupancy",
    "Casualty",
    "ChargeConnectorOccupancy",
    "ChargeConnectorOccupancyArray",
    "Crowding",
    "DbGeography",
    "DbGeographyWellKnownValue",
    "Disambiguation",
    "DisambiguationOption",
    "DisruptedPoint",
    "DisruptedPointArray",
    "Disruption",
    "DisruptionArray",
    "Fare",
    "FareCaveat",
    "FareTap",
    "FareTapDetails",
    "Identifier",
    "Instruction",
    "InstructionStep",
    "Interval",
    "ItineraryResult",
    "Journey",
    "JourneyFare",
    "JourneyPlannerCycleHireDockingStationData",
    "JourneyVector",
    "JpElevation",
    "KnownJourney",
    "Leg",
    "LiftDisruption",
    "LiftDisruptionsArray",
    "Line",
    "LineArray",
    "LineGroup",
    "LineModeGroup",
    "LineRouteSection",
    "LineServiceType",
    "LineServiceTypeArray",
    "LineServiceTypeInfo",
    "LineSpecificServiceType",
    "LineStatus",
    "LondonAirForecast",
    "MatchedRoute",
    "MatchedRouteSections",
    "MatchedStop",
    "Mode",
    "ModeArray",
    "Object",
    "ObjectResponse",
    "Obstacle",
    "OrderedRoute",
    "PassengerFlow",
    "Path",
    "PathAttribute",
    "Period",
    "Place",
    "PlaceArray",
    "PlaceCategory",
    "PlaceCategoryArray",
    "PlannedWork",
    "Point",
    "Prediction",
    "PredictionArray",
    "PredictionTiming",
    "RoadCorridor",
    "RoadCorridorsArray",
    "RoadDisruption",
    "RoadDisruptionImpactArea",
    "RoadDisruptionLine",
    "RoadDisruptionSchedule",
    "RoadDisruptionsArray",
    "RoadProject",
    "RouteOption",
    "RouteSearchMatch",
    "RouteSearchResponse",
    "RouteSection",
    "RouteSectionNaptanEntrySequence",
    "RouteSequence",
    "Schedule",
    "SearchCriteria",
    "SearchMatch",
    "SearchResponse",
    "ServiceFrequency",
    "StationInterval",
    "StatusSeveritiesArray",
    "StatusSeverity",
    "StopPoint",
    "StopPointArray",
    "StopPointRouteSection",
    "StopPointRouteSectionArray",
    "StopPointSequence",
    "StopPointsResponse",
    "Street",
    "StreetSegment",
    "StringsArray",
    "TimeAdjustment",
    "TimeAdjustments",
    "Timetable",
    "TimetableResponse",
    "TimetableRoute",
    "TrainLoading",
    "TwentyFourHourClockTime",
    "ValidityPeriod",
    "Vehicle",
    "VehicleMatch"
]

__all__ = [
    "AccidentDetail",
    "AccidentDetailArray",
    "ActiveServiceType",
    "ActiveServiceTypesArray",
    "AdditionalProperties",
    "ArrivalDeparture",
    "ArrivalDepartureArray",
    "Bay",
    "BikePointOccupancy",
    "BikePointOccupancyArray",
    "CarParkOccupancy",
    "Casualty",
    "ChargeConnectorOccupancy",
    "ChargeConnectorOccupancyArray",
    "Crowding",
    "DbGeography",
    "DbGeographyWellKnownValue",
    "Disambiguation",
    "DisambiguationOption",
    "DisruptedPoint",
    "DisruptedPointArray",
    "Disruption",
    "DisruptionArray",
    "Fare",
    "FareCaveat",
    "FareTap",
    "FareTapDetails",
    "Identifier",
    "Instruction",
    "InstructionStep",
    "Interval",
    "ItineraryResult",
    "Journey",
    "JourneyFare",
    "JourneyPlannerCycleHireDockingStationData",
    "JourneyVector",
    "JpElevation",
    "KnownJourney",
    "Leg",
    "LiftDisruption",
    "LiftDisruptionsArray",
    "Line",
    "LineArray",
    "LineGroup",
    "LineModeGroup",
    "LineRouteSection",
    "LineServiceType",
    "LineServiceTypeArray",
    "LineServiceTypeInfo",
    "LineSpecificServiceType",
    "LineStatus",
    "LondonAirForecast",
    "MatchedRoute",
    "MatchedRouteSections",
    "MatchedStop",
    "Mode",
    "ModeArray",
    "Object",
    "ObjectResponse",
    "Obstacle",
    "OrderedRoute",
    "PassengerFlow",
    "Path",
    "PathAttribute",
    "Period",
    "Place",
    "PlaceArray",
    "PlaceCategory",
    "PlaceCategoryArray",
    "PlannedWork",
    "Point",
    "Prediction",
    "PredictionArray",
    "PredictionTiming",
    "RoadCorridor",
    "RoadCorridorsArray",
    "RoadDisruption",
    "RoadDisruptionImpactArea",
    "RoadDisruptionLine",
    "RoadDisruptionSchedule",
    "RoadDisruptionsArray",
    "RoadProject",
    "RouteOption",
    "RouteSearchMatch",
    "RouteSearchResponse",
    "RouteSection",
    "RouteSectionNaptanEntrySequence",
    "RouteSequence",
    "Schedule",
    "SearchCriteria",
    "SearchMatch",
    "SearchResponse",
    "ServiceFrequency",
    "StationInterval",
    "StatusSeveritiesArray",
    "StatusSeverity",
    "StopPoint",
    "StopPointArray",
    "StopPointRouteSection",
    "StopPointRouteSectionArray",
    "StopPointSequence",
    "StopPointsResponse",
    "Street",
    "StreetSegment",
    "StringsArray",
    "TimeAdjustment",
    "TimeAdjustments",
    "Timetable",
    "TimetableResponse",
    "TimetableRoute",
    "TrainLoading",
    "TwentyFourHourClockTime",
    "ValidityPeriod",
    "Vehicle",
    "VehicleMatch",
    'GenericResponseModel'
]
