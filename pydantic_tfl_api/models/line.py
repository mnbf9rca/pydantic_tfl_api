from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from .disruption import Disruption
from .line_status import LineStatus
from .route_section import RouteSection
from .service_type import ServiceType
from .crowding import Crowding


class Line(BaseModel):
    id: str = Field(alias='id')
    name: str = Field(alias='name')
    mode_name: Optional[str] = Field(None, alias='modeName')
    disruptions: Optional[List[Disruption]] = Field([], alias='disruptions')
    created: Optional[datetime] = Field(None, alias='created')
    modified: Optional[datetime] = Field(None, alias='modified')
    line_statuses: Optional[List[LineStatus]] = Field(None, alias='lineStatuses')
    route_sections: Optional[List[RouteSection]] = Field(None, alias='routeSections')
    service_types: Optional[List[ServiceType]] = Field(None, alias='serviceTypes')
    crowding: Optional[Crowding] = Field(None, alias='crowding')
    content_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}
