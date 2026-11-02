from pydantic import BaseModel, model_validator, Field, ConfigDict
from typing import Literal, Optional

class ReportCreate(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)
    listing_id: int
    reason: str = Field(min_length=1, max_length=500)


class ReportAccess(BaseModel):

    model_config = ConfigDict(str_strip_whitespace=True)

    resolution: Optional[str] = Field(default=None, max_length=500)
    action: Literal["hide", "dismiss"]

    @model_validator(mode="after")
    def status_check(self):
        if self.action == "hide" and not self.resolution:
            raise ValueError("Поле для записи причины решения не может быть пустым")
        return self


class ReportResponse(BaseModel):

    id: int
    user_id: int
    listing_id: int
    reason: str
    status: str
    resolution: Optional[str] = Field(default=None, max_length=500)
    model_config={"from_attributes": True}