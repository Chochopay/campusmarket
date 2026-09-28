from pydantic import BaseModel

class CategoryResponse(BaseModel):
    id: int
    name: str
    model_config = {"from_attributes" : True}