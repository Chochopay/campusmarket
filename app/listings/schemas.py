from pydantic import BaseModel, Field, model_validator
from decimal import Decimal
from typing import List, Literal, Optional


class ListingImageResponse(BaseModel):

    id: int
    img_file: str
    position: int


class ListingCreate(BaseModel):

    name: str = Field(max_length=100)
    description: str = Field(max_length=1000)
    condition: Literal ["new", "used"]
    mode: Literal ["sale", "exchange", "free"]
    price: Optional[Decimal] = None
    category_id: int

    @model_validator(mode="after")
    def validate_price_by_mode(self):
        if self.mode == "sale" and (self.price is None or self.price <= 0 ):
            raise ValueError("для режима 'продажа' цена должна быть положительной")
        if self.mode == "exchange" and (self.price is not None and self.price != 0):
            raise ValueError("для режима 'обмен' цена должна отсутствовать")
        if self.mode == "free" and self.price not in (0, None):
            raise ValueError("для режима 'бесплатно' цена должна равняться нулю или отсутствовать")
        return self


class ListingUpdate(BaseModel):

    name: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = Field(default=None, max_length=1000)
    condition: Optional[Literal["new", "used"]] = None
    mode: Optional[Literal["sale", "exchange", "free"]] = None
    price: Optional[Decimal] = None
    category_id: Optional[int] = None
    status: Optional[Literal["published", "unpublished"]] = None


class ListingResponse(BaseModel):

    id: int
    name: str
    description: str
    status: str
    condition: str
    mode: str
    price: Optional[Decimal] = None
    category_id: int
    user_id: int
    listing_images: List[ListingImageResponse]
    model_config = {"from_attributes":True}


