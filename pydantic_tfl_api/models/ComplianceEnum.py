from enum import Enum


class ComplianceEnum(Enum):
    NOTAVAILABLE = 'NotAvailable'
    NOTCOMPLIANT = 'NotCompliant'
    COMPLIANT = 'Compliant'
    EXEMPT = 'Exempt'
