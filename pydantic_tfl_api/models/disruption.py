from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional

from .affected_route import AffectedRoute
from .stop_point import StopPoint


class Disruption(BaseModel):
    category: str = Field(alias='category')
    disruption_type: str = Field(alias='type')
    category_description: str = Field(alias='categoryDescription')
    description: str = Field(alias='description')
    summary: Optional[str] = Field(None, alias='summary')
    additional_info: Optional[str] = Field(None, alias='additionalInfo')
    created: Optional[datetime] = Field(None, alias='created')
    last_update: Optional[datetime] = Field(None, alias='lastUpdate')
    affected_routes: List[AffectedRoute] = Field(alias='affectedRoutes')
    affected_stops: List[StopPoint] = Field(alias='affectedStops')
    closure_text: str = Field(alias='closureText')
    content_expires: Optional[datetime] = Field(None)
    shared_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}

    