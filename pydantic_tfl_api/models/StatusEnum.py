from enum import Enum


class StatusEnum(Enum):
    UNKNOWN = 'Unknown'
    ALL = 'All'
    OPEN = 'Open'
    IN_PROGRESS = 'In Progress'
    PLANNED = 'Planned'
    PLANNED___SUBJECT_TO_FEASIBILITY_AND_CONSULTATION = 'Planned - Subject to feasibility and consultation.'
    NOT_OPEN = 'Not Open'
