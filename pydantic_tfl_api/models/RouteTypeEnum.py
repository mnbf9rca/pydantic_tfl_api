from enum import Enum


class RouteTypeEnum(Enum):
    UNKNOWN = 'Unknown'
    ALL = 'All'
    CYCLE_SUPERHIGHWAYS = 'Cycle Superhighways'
    QUIETWAYS = 'Quietways'
    CYCLEWAYS = 'Cycleways'
    MINI_HOLLANDS = 'Mini-Hollands'
    CENTRAL_LONDON_GRID = 'Central London Grid'
    STREETSPACE_ROUTE = 'Streetspace Route'
