from .InstructionStep import InstructionStep
from pydantic import BaseModel, Field
from typing import List, Optional


class Instruction(BaseModel):
    summary: Optional[str] = Field(None, alias='summary')
    detailed: Optional[str] = Field(None, alias='detailed')
    steps: Optional[list[InstructionStep]] = Field(None, alias='steps')

    model_config = {'from_attributes': True}
