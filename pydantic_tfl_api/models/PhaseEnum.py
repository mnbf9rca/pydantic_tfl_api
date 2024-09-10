from enum import Enum


class PhaseEnum(Enum):
    UNSCOPED = 'Unscoped'
    CONCEPT = 'Concept'
    CONSULTATIONENDED = 'ConsultationEnded'
    CONSULTATION = 'Consultation'
    CONSTRUCTION = 'Construction'
    COMPLETE = 'Complete'
