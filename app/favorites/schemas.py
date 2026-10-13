from pydantic import BaseModel


class FavoriteAdd(BaseModel):
    listing_id: int


class FavoriteResponse(BaseModel):
    id: int
    user_id: int
    listing_id: int
    model_config={"from_attributes": True}