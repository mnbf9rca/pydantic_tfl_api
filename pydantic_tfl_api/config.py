# from https://github.com/dhilmathy/TfL-python-api
# MIT License

# Copyright (c) 2018 Mathivanan Palanisamy

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

base_url = "https://api.tfl.gov.uk/"

# missing:
# Line_RouteByQueryServiceTypes /Line/Route[?serviceTypes]
# Line_LineRoutesByIdsByPathIdsQueryServiceTypes /Line/{ids}/Route[?serviceTypes]
# Line_ArrivalsWithStopPointByPathIdsPathStopPointIdQueryDirectionQueryDestina /Line/{ids}/Arrivals/{stopPointId}[?direction][&destinationStationId]
# Line_StopPointsByPathIdQueryTflOperatedNationalRailStationsOnly /Line/{id}/StopPoints[?tflOperatedNationalRailStationsOnly]
# Line_MetaDisruptionCategories /Line/Meta/DisruptionCategories
# Line_MetaServiceTypes /Line/Meta/ServiceTypes
# Line_MetaSeverity /Line/Meta/Severity
# Line_StatusByPathIdsPathStartDatePathEndDateQueryDetail /Line/{ids}/Status/{startDate}/to/{endDate}[?detail]
# Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel /Line/Mode/{modes}/Status[?detail][&severityLevel]
# Line_TimetableByPathFromStopPointIdPathId /Line/{id}/Timetable/{fromStopPointId}
# Line_TimetableToByPathFromStopPointIdPathIdPathToStopPointId /Line/{id}/Timetable/{fromStopPointId}/to/{toStopPointId}




endpoints = {
    'stopPointsByLineId': {"uri": 'Line/{0}/StopPoints', "model" : "StopPoint"},
    'Line_MetaModes': {"uri": 'Line/Meta/Modes', "model" : "Mode"},
    'Line_GetByPathIds': {"uri": 'Line/{0}', "model" : "Line"},
    'Line_GetByModeByPathModes': {"uri": 'Line/Mode/{0}', "model" : "Line"},
    'Line_StatusByIdsByPathIdsQueryDetail': {"uri": 'Line/{0}/Status', "model" : "Line"},
    'Line_StatusBySeverityByPathSeverity': {"uri": 'Line/Status/{0}', "model" : "Line"},
    'Line_StatusByModeByPathModesQueryDetailQuerySeverityLevel': {"uri": 'Line/Mode/{0}/Status', "model" : "Line"},
    'Line_LineRoutesByIdsByPathIdsQueryServiceTypes': {"uri": 'Line/{0}/Route', "model" : "Line"},
    'Line_RouteSequenceByPathIdPathDirectionQueryServiceTypesQueryExcludeCrowding': {"uri": 'Line/{0}/Route/Sequence/{1}', "model" : "RouteSequence"},
    'Line_RouteByModeByPathModesQueryServiceTypes': {"uri": 'Line/Mode/{0}/Route', "model" : "Line"},
    'Line_DisruptionByPathIds': {"uri": 'Line/{0}/Disruption', "model" : "Disruption"},
    'Line_DisruptionByModeByPathModes': {"uri": 'Line/Mode/{0}/Disruption', "model" : "Disruption"},

    'stopPointMetaModes': {"uri": 'StopPoint/Meta/Modes', "model" : "Mode"},
    'stopPointById': {"uri":  'StopPoint/{0}', "model" : "StopPoint"},
    'stopPointByMode':  {"uri": 'StopPoint/Mode/{0}', "model" : "StopPointsResponse"},
    'Line_ArrivalsByPathIds': {"uri": 'Line/{0}/Arrivals', "model" : "Prediction"}
}
