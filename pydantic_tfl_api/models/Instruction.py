from pydantic import BaseModel, ConfigDict, Field

from .InstructionStep import InstructionStep


class Instruction(BaseModel):
    summary: str | None = Field(None)
    detailed: str | None = Field(None)
    steps: list[InstructionStep] | None = Field(None)

    model_config = ConfigDict(from_attributes=True)
