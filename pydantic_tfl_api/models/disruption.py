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
    summary: str = Field(alias='summary')
    additional_info: str = Field(alias='additionalInfo')
    created: datetime = Field(alias='created')
    last_update: datetime = Field(alias='lastUpdate')
    affected_routes: List[AffectedRoute] = Field(alias='affectedRoutes')
    affected_stops: List[StopPoint] = Field(alias='affectedStops')
    closure_text: str = Field(alias='closureText')
    content_expires: Optional[datetime] = Field(None)

    model_config = {'populate_by_name': True}

    