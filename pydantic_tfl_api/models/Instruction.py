from .InstructionStep import InstructionStep
from pydantic import BaseModel, Field, ConfigDict


class Instruction(BaseModel):
    summary: str | None = Field(None)
    detailed: str | None = Field(None)
    steps: list[InstructionStep] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
