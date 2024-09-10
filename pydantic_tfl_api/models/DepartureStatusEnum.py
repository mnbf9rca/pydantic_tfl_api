from enum import Enum


class DepartureStatusEnum(Enum):
    ONTIME = 'OnTime'
    DELAYED = 'Delayed'
    CANCELLED = 'Cancelled'
    NOTSTOPPINGATSTATION = 'NotStoppingAtStation'
