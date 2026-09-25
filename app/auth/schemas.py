from pydantic import BaseModel, Field

class UserCreate(BaseModel):
    username: str = Field(min_length=4, max_length=20)
    password: str = Field(min_length=8, max_length=64)


class UserResponse(BaseModel):
    id: int
    username: str
    role: str

    model_config={"from_attributes" : True}


class UserLogin(BaseModel):
    username: str
    password: str


class UserLoginResponse(BaseModel):
    jwt_token: str
