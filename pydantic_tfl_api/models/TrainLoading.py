from pydantic import BaseModel, ConfigDict, Field


class TrainLoading(BaseModel):
    line: str | None = Field(None, description="The Line Name e.g. \"Victoria\"")
    lineDirection: str | None = Field(None, description="Direction of the Line e.g. NB, SB, WB etc.")
    platformDirection: str | None = Field(None, description="Direction displayed on the platform e.g. NB, SB, WB etc.")
    direction: str | None = Field(None, description="Direction in regards to Journey Planner i.e. inbound or outbound")
    naptanTo: str | None = Field(None, description="Naptan of the adjacent station")
    timeSlice: str | None = Field(None, description="Time in 24hr format with 15 minute intervals e.g. 0500-0515, 0515-0530 etc.")
    value: int | None = Field(None, description="Scale between 1-6, 1 = Very quiet, 2 = Quiet, 3 = Fairly busy, 4 = Busy, 5 = Very busy, 6 = Exceptionally busy")

    model_config = ConfigDict(from_attributes=True)
