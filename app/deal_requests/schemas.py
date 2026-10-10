from pydantic import BaseModel, Field

class DealRequestResponse(BaseModel):

    id: int
    listing_id: int
    buyer_id: int
    status: str
    text: str
    model_config={"from_attributes": True}


class DealRequestCreate(BaseModel):

    text: str = Field(max_length=500)
