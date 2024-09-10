from enum import Enum


class CategoryEnum(Enum):
    UNDEFINED = 'Undefined'
    REALTIME = 'RealTime'
    PLANNEDWORK = 'PlannedWork'
    INFORMATION = 'Information'
    EVENT = 'Event'
    CROWDING = 'Crowding'
    STATUSALERT = 'StatusAlert'
