from pydantic import BaseModel, Field, ConfigDict
from datetime import datetime

class MessageCreate(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    text: str = Field(min_length=1, max_length=500)


class MessageResponse(BaseModel):
    id: int
    request_id: int
    text: str
    sender_id: int
    created_at: datetime
    model_config={"from_attributes": True}
