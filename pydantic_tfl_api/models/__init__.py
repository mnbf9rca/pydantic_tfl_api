from typing import Literal

from .ActiveServiceType import ActiveServiceType
from .ActiveServiceTypesArray import ActiveServiceTypesArray
from .AdditionalProperties import AdditionalProperties
from .Bay import Bay
from .BikePointOccupancy import BikePointOccupancy
from .BikePointOccupancyArray import BikePointOccupancyArray
from .CarParkOccupancy import CarParkOccupancy
from .Casualty import Casualty
from .ChargeConnectorOccupancy import ChargeConnectorOccupancy
from .ChargeConnectorOccupancyArray import ChargeConnectorOccupancyArray
from .DbGeographyWellKnownValue import DbGeographyWellKnownValue
from .DbGeography import DbGeography
from .DisambiguationOption import DisambiguationOption
from .Disambiguation import Disambiguation
from .DisruptedPoint import DisruptedPoint
from .DisruptedPointArray import DisruptedPointArray
from .FareCaveat import FareCaveat
from .FareTapDetails import FareTapDetails
from .FareTap import FareTap
from .Fare import Fare
from .Interval import Interval
from .JourneyFare import JourneyFare
from .JourneyPlannerCycleHireDockingStationData import JourneyPlannerCycleHireDockingStationData
from .JourneyVector import JourneyVector
from .JpElevation import JpElevation
from .KnownJourney import KnownJourney
from .LiftDisruption import LiftDisruption
from .LiftDisruptionsArray import LiftDisruptionsArray
from .LineGroup import LineGroup
from .LineModeGroup import LineModeGroup
from .LineRouteSection import LineRouteSection
from .LineServiceTypeInfo import LineServiceTypeInfo
from .LineSpecificServiceType import LineSpecificServiceType
from .LineServiceType import LineServiceType
from .LineServiceTypeArray import LineServiceTypeArray
from .LondonAirForecast import LondonAirForecast
from .MatchedRoute import MatchedRoute
from .MatchedRouteSections import MatchedRouteSections
from .Mode import Mode
from .ModeArray import ModeArray
from .Object import Object
from .ObjectResponse import ObjectResponse
from .Obstacle import Obstacle
from .OrderedRoute import OrderedRoute
from .PassengerFlow import PassengerFlow
from .PathAttribute import PathAttribute
from .InstructionStep import InstructionStep
from .Instruction import Instruction
from .PlaceCategory import PlaceCategory
from .PlaceCategoryArray import PlaceCategoryArray
from .PlannedWork import PlannedWork
from .Point import Point
from .PredictionTiming import PredictionTiming
from .ArrivalDeparture import ArrivalDeparture
from .ArrivalDepartureArray import ArrivalDepartureArray
from .Prediction import Prediction
from .PredictionArray import PredictionArray
from .RoadCorridor import RoadCorridor
from .RoadCorridorsArray import RoadCorridorsArray
from .RoadDisruptionImpactArea import RoadDisruptionImpactArea
from .RoadDisruptionLine import RoadDisruptionLine
from .RoadDisruptionSchedule import RoadDisruptionSchedule
from .RoadProject import RoadProject
from .SearchMatch import SearchMatch
from .SearchResponse import SearchResponse
from .ServiceFrequency import ServiceFrequency
from .StationInterval import StationInterval
from .StatusSeverity import StatusSeverity
from .StatusSeveritiesArray import StatusSeveritiesArray
from .StopPointRouteSection import StopPointRouteSection
from .StopPointRouteSectionArray import StopPointRouteSectionArray
from .StreetSegment import StreetSegment
from .Street import Street
from .RoadDisruption import RoadDisruption
from .RoadDisruptionsArray import RoadDisruptionsArray
from .StringsArray import StringsArray
from .TimeAdjustment import TimeAdjustment
from .TimeAdjustments import TimeAdjustments
from .SearchCriteria import SearchCriteria
from .TrainLoading import TrainLoading
from .Crowding import Crowding
from .Identifier import Identifier
from .MatchedStop import MatchedStop
from .Path import Path
from .RouteOption import RouteOption
from .RouteSearchMatch import RouteSearchMatch
from .RouteSearchResponse import RouteSearchResponse
from .StopPointSequence import StopPointSequence
from .RouteSequence import RouteSequence
from .TwentyFourHourClockTime import TwentyFourHourClockTime
from .Period import Period
from .Schedule import Schedule
from .TimetableRoute import TimetableRoute
from .Timetable import Timetable
from .TimetableResponse import TimetableResponse
from .ValidityPeriod import ValidityPeriod
from .Vehicle import Vehicle
from .AccidentDetail import AccidentDetail
from .AccidentDetailArray import AccidentDetailArray
from .VehicleMatch import VehicleMatch
from .Disruption import Disruption
from .DisruptionArray import DisruptionArray
from .ItineraryResult import ItineraryResult
from .Journey import Journey
from .Leg import Leg
from .Line import Line
from .LineArray import LineArray
from .LineStatus import LineStatus
from .Place import Place
from .PlaceArray import PlaceArray
from .RouteSection import RouteSection
from .RouteSectionNaptanEntrySequence import RouteSectionNaptanEntrySequence
from .StopPoint import StopPoint
from .StopPointArray import StopPointArray
from .StopPointsResponse import StopPointsResponse

from ..core.package_models import GenericResponseModel

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
    "VehicleMatch",
    "GenericResponseModel"
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
